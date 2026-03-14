const { weighNumRange, date } = require('/Users/ninad/.npm/_npx/7ffc192268bff7fa/node_modules/make-mp-data/lib/utils/utils.js');

/** @type {import('/Users/ninad/.npm/_npx/7ffc192268bff7fa/node_modules/make-mp-data/types').Dungeon} */
module.exports = {
  token: '33fefd877297ff1c97e1ac7a8137b594',
  seed: 'ninad-funnel-demo-2026-03-12',
  numDays: 45,
  numUsers: 10000,
  numEvents: 180000,
  format: 'csv',
  region: 'US',
  hasAnonIds: false,
  hasSessionIds: true,
  hasLocation: true,
  hasAndroidDevices: false,
  hasIOSDevices: false,
  hasDesktopDevices: true,
  hasBrowser: true,
  hasCampaigns: true,
  hasAdSpend: true,
  isAnonymous: false,
  alsoInferFunnels: false,
  batchSize: 500000,
  concurrency: 40,
  writeToDisk: true,
  funnels: [
    {
      name: 'Account Activation',
      sequence: ['Account Created', 'Email Verified', 'Workspace Created'],
      conversionRate: 78,
      order: 'sequential',
      weight: 10
    },
    {
      name: 'Core Product Setup',
      sequence: ['Workspace Created', 'Project Created', 'Dashboard Viewed', 'Report Generated'],
      conversionRate: 61,
      order: 'sequential',
      weight: 9
    },
    {
      name: 'Team Collaboration',
      sequence: ['Report Generated', 'Integration Connected', 'Team Member Invited', 'Invite Accepted'],
      conversionRate: 42,
      order: 'sequential',
      weight: 7
    },
    {
      name: 'Paid Conversion',
      sequence: ['Pricing Viewed', 'Checkout Started', 'Payment Added', 'Subscription Started'],
      conversionRate: 24,
      order: 'sequential',
      weight: 6
    },
    {
      name: 'Retention Signal',
      sequence: ['Dashboard Viewed', 'Saved Segment Created', 'Alert Created', 'Report Shared'],
      conversionRate: 33,
      order: 'sequential',
      weight: 5
    }
  ],
  events: [
    {
      event: 'Account Created',
      isFirstEvent: true,
      weight: 0,
      properties: {
        signup_method: ['email', 'google', 'github'],
        landing_page: ['/home', '/product', '/compare', '/pricing']
      }
    },
    {
      event: 'Email Verified',
      weight: 18,
      properties: {
        verification_method: ['magic_link', 'otp', 'email_link']
      }
    },
    {
      event: 'Workspace Created',
      weight: 20,
      properties: {
        workspace_type: ['marketing', 'product', 'sales', 'support'],
        industry: ['saas', 'ecommerce', 'fintech', 'healthcare', 'agency']
      }
    },
    {
      event: 'Project Created',
      weight: 18,
      properties: {
        project_template: ['blank', 'growth', 'sales', 'retention', 'executive']
      }
    },
    {
      event: 'Dashboard Viewed',
      weight: 45,
      properties: {
        dashboard_name: ['Overview', 'Activation', 'Revenue', 'Retention', 'Campaigns'],
        view_mode: ['default', 'saved', 'shared']
      }
    },
    {
      event: 'Report Generated',
      weight: 28,
      properties: {
        report_type: ['funnel', 'retention', 'conversion', 'cohort', 'attribution'],
        query_time_ms: weighNumRange(100, 3500, 0.25)
      }
    },
    {
      event: 'Saved Segment Created',
      weight: 16,
      properties: {
        segment_type: ['power_users', 'new_signups', 'trial_users', 'high_intent_leads']
      }
    },
    {
      event: 'Alert Created',
      weight: 10,
      properties: {
        alert_type: ['conversion_drop', 'traffic_spike', 'revenue_change'],
        threshold_pct: weighNumRange(5, 40, 0.7)
      }
    },
    {
      event: 'Report Shared',
      weight: 12,
      properties: {
        share_channel: ['email', 'slack', 'link'],
        recipients: weighNumRange(1, 8, 0.5)
      }
    },
    {
      event: 'Integration Connected',
      weight: 14,
      properties: {
        integration: ['salesforce', 'hubspot', 'stripe', 'shopify', 'zendesk']
      }
    },
    {
      event: 'Team Member Invited',
      weight: 12,
      properties: {
        role: ['admin', 'analyst', 'viewer']
      }
    },
    {
      event: 'Invite Accepted',
      weight: 9,
      properties: {
        role: ['admin', 'analyst', 'viewer']
      }
    },
    {
      event: 'Pricing Viewed',
      weight: 20,
      properties: {
        plan_considered: ['starter', 'growth', 'pro', 'enterprise']
      }
    },
    {
      event: 'Checkout Started',
      weight: 10,
      properties: {
        billing_period: ['monthly', 'annual']
      }
    },
    {
      event: 'Payment Added',
      weight: 8,
      properties: {
        payment_method: ['card', 'invoice']
      }
    },
    {
      event: 'Subscription Started',
      weight: 7,
      properties: {
        plan: ['starter', 'growth', 'pro', 'enterprise'],
        billing_period: ['monthly', 'annual'],
        mrr: weighNumRange(29, 499, 0.18)
      }
    },
    {
      event: 'Search Performed',
      weight: 22,
      properties: {
        query_length: weighNumRange(2, 30, 0.35)
      }
    },
    {
      event: 'Support Ticket Opened',
      weight: 4,
      properties: {
        severity: ['low', 'medium', 'high']
      }
    }
  ],
  superProps: {
    app_version: ['1.12.0', '1.13.0', '1.13.1'],
    acquisition_channel: ['organic', 'linkedin', 'google_ads', 'partner', 'product_hunt'],
    company_band: ['1-10', '11-50', '51-200', '201-1000', '1000+']
  },
  userProps: {
    persona: ['marketer', 'product_manager', 'founder', 'analyst', 'sales_lead'],
    plan_status: ['free', 'free', 'trial', 'paid', 'free'],
    signup_date: date(365, true, 'YYYY-MM-DD')
  },
  hook(record) {
    return record;
  }
};
