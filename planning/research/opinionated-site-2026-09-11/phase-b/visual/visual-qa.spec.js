const path = require("path");
const { test, expect } = require("@playwright/test");

const pages = [
  {
    slug: "developer-onboarding-docs-what-works-what-doesnt",
    artifact: "onboarding",
    imageCount: 2,
  },
  {
    slug: "documentation-review-checklist-before-you-publish",
    artifact: "review",
    imageCount: 0,
  },
  {
    slug: "documentation-style-guide-template",
    artifact: "style-guide",
    imageCount: 0,
  },
  {
    slug: "how-to-organize-a-documentation-site",
    artifact: "organization",
    imageCount: 1,
  },
];

async function settleViewport(page) {
  await page.evaluate(() => new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  }));
}

for (const entry of pages) {
  test(`${entry.artifact} current render`, async ({ page }, testInfo) => {
    await page.goto(`/articles/${entry.slug}/`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);

    const articleImages = page.locator(".post-content img");
    await expect(articleImages).toHaveCount(entry.imageCount);
    await articleImages.evaluateAll((nodes) => {
      for (const image of nodes) image.loading = "eager";
    });
    for (let index = 0; index < entry.imageCount; index += 1) {
      const image = articleImages.nth(index);
      await expect.poll(
        () => image.evaluate((node) => node.complete && node.naturalWidth > 0 && node.naturalHeight > 0),
        { timeout: 10_000 },
      ).toBe(true);
    }
    const scrollPosition = await page.evaluate(() => ({
      windowY: window.scrollY,
      documentTop: document.scrollingElement.scrollTop,
    }));
    expect(scrollPosition.windowY).toBe(0);
    expect(scrollPosition.documentTop).toBe(0);

    const images = await page.locator(".post-content img").evaluateAll((nodes) =>
      nodes.map((image, index) => ({
        index,
        src: image.getAttribute("src"),
        complete: image.complete,
        naturalWidth: image.naturalWidth,
        naturalHeight: image.naturalHeight,
        renderedWidth: image.getBoundingClientRect().width,
        renderedHeight: image.getBoundingClientRect().height,
        renderedRatio: image.getBoundingClientRect().width / image.getBoundingClientRect().height,
        naturalRatio: image.naturalWidth / image.naturalHeight,
        container: (() => {
          const container = image.closest(".visual-container");
          if (!container) return null;
          const imageRect = image.getBoundingClientRect();
          const containerRect = container.getBoundingClientRect();
          return {
            width: containerRect.width,
            height: containerRect.height,
            fits:
              imageRect.left >= containerRect.left - 1 &&
              imageRect.right <= containerRect.right + 1 &&
              imageRect.top >= containerRect.top - 1 &&
              imageRect.bottom <= containerRect.bottom + 1,
          };
        })(),
      })),
    );
    for (const image of images) {
      expect(image.complete).toBe(true);
      expect(image.naturalWidth).toBeGreaterThan(0);
      expect(image.naturalHeight).toBeGreaterThan(0);
      expect(Math.abs(image.renderedRatio - image.naturalRatio)).toBeLessThan(0.01);
      expect(image.container).not.toBeNull();
      expect(image.container.fits).toBe(true);
      expect(Math.abs(image.container.height - image.renderedHeight)).toBeLessThan(1);
    }

    const pageWidth = await page.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    expect(pageWidth.scrollWidth).toBeLessThanOrEqual(pageWidth.clientWidth);

    const artifacts = [];
    if (testInfo.project.name === "desktop") {
      const artifact = `${entry.artifact}-desktop.png`;
      await page.screenshot({
        path: path.join(__dirname, artifact),
        fullPage: true,
      });
      artifacts.push(artifact);
    } else {
      await page.evaluate(() => window.scrollTo(0, 0));
      await settleViewport(page);
      const header = await page.locator(".nav").boundingBox();
      const logo = await page.locator(".nav > .nav-inner > .nav-logo").boundingBox();
      expect(header.x).toBe(0);
      expect(header.width).toBe(390);
      expect(logo.x).toBe(24);
      const topArtifact = `${entry.artifact}-mobile-top.png`;
      await page.screenshot({
        path: path.join(__dirname, topArtifact),
        clip: { x: 0, y: 0, width: 390, height: 844 },
        captureBeyondViewport: false,
      });
      artifacts.push(topArtifact);

      for (let index = 0; index < images.length; index += 1) {
        const image = articleImages.nth(index);
        const wrapper = image.locator("xpath=ancestor::div[contains(@class, 'visual-wrapper')]");
        await wrapper.scrollIntoViewIfNeeded();
        await settleViewport(page);
        const artifact = `${entry.artifact}-mobile-image-${index + 1}.png`;
        await page.screenshot({
          path: path.join(__dirname, artifact),
        });
        artifacts.push(artifact);
      }
    }

    let tables = [];
    if (testInfo.project.name === "mobile") {
      const tableLocators = page.locator(".post-content table");
      const tableCount = await tableLocators.count();
      for (let index = 0; index < tableCount; index += 1) {
        const table = tableLocators.nth(index);
        const record = await table.evaluate((node, tableIndex) => {
          const label = [...node.querySelectorAll("thead th")]
            .map((cell) => cell.textContent.trim())
            .join(" | ");
          node.scrollLeft = 0;
          return {
            index: tableIndex,
            label,
            clientWidth: node.clientWidth,
            scrollWidth: node.scrollWidth,
            before: node.scrollLeft,
            overflow: node.scrollWidth > node.clientWidth + 1,
          };
        }, index);
        if (!record.overflow) {
          tables.push({ ...record, after: 0, moved: false, artifacts: [] });
          continue;
        }

        await table.scrollIntoViewIfNeeded();
        await settleViewport(page);
        const beforeArtifact = `${entry.artifact}-mobile-table-${index + 1}-before.png`;
        await page.screenshot({
          path: path.join(__dirname, beforeArtifact),
        });
        const after = await table.evaluate((node) => {
          node.scrollLeft = node.scrollWidth;
          return node.scrollLeft;
        });
        await settleViewport(page);
        const moved = after > record.before;
        expect(moved).toBe(true);
        const afterArtifact = `${entry.artifact}-mobile-table-${index + 1}-after.png`;
        await page.screenshot({
          path: path.join(__dirname, afterArtifact),
        });
        artifacts.push(beforeArtifact, afterArtifact);
        tables.push({
          ...record,
          after,
          moved,
          artifacts: [beforeArtifact, afterArtifact],
        });
      }
    }

    console.log(`PHASE_B_VISUAL_QA ${JSON.stringify({
      article: entry.artifact,
      viewport: testInfo.project.name,
      pageWidth,
      scrollPosition,
      images,
      tables,
      artifacts,
    })}`);
  });
}

test("representative unaffected article imagery", async ({ page }, testInfo) => {
  await page.goto("/articles/internal-vs-external-documentation/", { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const flowchart = page.locator(".flowchart-image img");
  await flowchart.scrollIntoViewIfNeeded();
  await expect.poll(
    () => flowchart.evaluate((image) => image.complete && image.naturalWidth > 0 && image.naturalHeight > 0),
    { timeout: 10_000 },
  ).toBe(true);
  await settleViewport(page);
  const flowchartLayout = await flowchart.evaluate((image) => {
    const imageRect = image.getBoundingClientRect();
    const pictureRect = image.closest("picture").getBoundingClientRect();
    return {
      complete: image.complete,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      renderedWidth: imageRect.width,
      renderedHeight: imageRect.height,
      ratioDifference: Math.abs(
        imageRect.width / imageRect.height - image.naturalWidth / image.naturalHeight,
      ),
      fits:
        imageRect.left >= pictureRect.left - 1 &&
        imageRect.right <= pictureRect.right + 1 &&
        imageRect.top >= pictureRect.top - 1 &&
        imageRect.bottom <= pictureRect.bottom + 1,
    };
  });
  expect(flowchartLayout.ratioDifference).toBeLessThan(0.01);
  expect(flowchartLayout.fits).toBe(true);
  const flowchartArtifact = `unaffected-flowchart-${testInfo.project.name}.png`;
  await page.screenshot({ path: path.join(__dirname, flowchartArtifact) });

  await page.goto("/articles/agent-harnesses/", { waitUntil: "networkidle" });
  const iframe = page.locator(".visual-container iframe").first();
  await iframe.scrollIntoViewIfNeeded();
  await settleViewport(page);
  const iframeLayout = await iframe.evaluate((frame) => {
    const frameRect = frame.getBoundingClientRect();
    const containerRect = frame.parentElement.getBoundingClientRect();
    return {
      frameWidth: frameRect.width,
      frameHeight: frameRect.height,
      containerWidth: containerRect.width,
      containerHeight: containerRect.height,
      fits:
        Math.abs(frameRect.width - containerRect.width) < 1 &&
        Math.abs(frameRect.height - containerRect.height) < 1,
    };
  });
  expect(iframeLayout.fits).toBe(true);
  expect(iframeLayout.containerHeight).toBe(testInfo.project.name === "mobile" ? 500 : 400);
  const iframeArtifact = `unaffected-iframe-${testInfo.project.name}.png`;
  await page.screenshot({ path: path.join(__dirname, iframeArtifact) });

  console.log(`PHASE_B_UNAFFECTED_VISUAL_QA ${JSON.stringify({
    viewport: testInfo.project.name,
    flowchart: flowchartLayout,
    iframe: iframeLayout,
    artifacts: [flowchartArtifact, iframeArtifact],
  })}`);
});
