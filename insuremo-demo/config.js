// API 配置
const CONFIG = {
    // API Base URL
    BASE_URL: 'https://portal-gw.insuremo.com/platform/api-orchestration-test',

    // Auth Token
    AUTH_TOKEN: 'MOATbWg4aRISAep86MorzeBulKla18sq',

    // 产品信息
    PRODUCT: {
        CODE: 'TRVL01',
        ID: 375604942,
        NAME: 'Travel Insurance'
    },

    // API 端点
    ENDPOINTS: {
        PRODUCT_LIST: '/v1/flow/EUDemoProductList',
        POLICY_SCHEMA: '/v1/flow/EUDemoPolicySchema',
        PLAN_LIST: '/v1/flow/EUDemoPlanList',
        CALCULATE: '/v1/flow/EUDemoTRVL01Calculate',
        SAVE_PROPOSAL: '/v1/flow/EUDemoTRVL01SaveProposal',
        BIND_PROPOSAL: '/v1/flow/EUDemoTRVL01BindProposal',
        PAYMENT_CALLBACK: '/v1/flow/EUDemoTRVL01PaymentCallback',
        POLICY: '/v1/flow/EUDemoTRVL01Policy'
    },

    // 默认值
    DEFAULTS: {
        CURRENCY: 'EUR',
        TRAVEL_POLICY_TYPE: 'INDI'
    }
};

// 不要修改此文件，配置项由系统管理
