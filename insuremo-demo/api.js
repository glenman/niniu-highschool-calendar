/**
 * InsureMO API 封装
 * 提供统一的 API 调用接口
 */

class InsureMOAPI {
    constructor() {
        this.baseUrl = CONFIG.BASE_URL;
        this.token = CONFIG.AUTH_TOKEN;
    }

    /**
     * 通用 API 调用方法
     */
    async call(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;

        const options = {
            method: method,
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            console.log(`📡 API Call: ${method} ${endpoint}`);
            
            const response = await fetch(url, options);
            
            console.log(`✅ Response Status: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ API Error Response:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const result = await response.json();
            console.log('📦 API Response:', result);

            if (!result.Success) {
                const errorMsg = result.Error?.Message || result.message || 'API call failed';
                throw new Error(errorMsg);
            }

            return result.Data;
        } catch (error) {
            console.error('❌ API Error:', error);
            
            // 提供更友好的错误信息
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('网络连接失败，请检查网络或API服务是否可用');
            } else if (error.message.includes('CORS')) {
                throw new Error('跨域请求被阻止，请联系管理员配置CORS');
            }
            
            throw error;
        }
    }

    /**
     * 获取产品列表
     */
    async getProductList() {
        return await this.call(CONFIG.ENDPOINTS.PRODUCT_LIST);
    }

    /**
     * 获取产品 Schema
     */
    async getPolicySchema(productId) {
        return await this.call(`${CONFIG.ENDPOINTS.POLICY_SCHEMA}?productId=${productId}`);
    }

    /**
     * 获取产品方案列表
     */
    async getPlanList(productId) {
        return await this.call(`${CONFIG.ENDPOINTS.PLAN_LIST}?productId=${productId}`);
    }

    /**
     * 计算保费
     */
    async calculatePremium(payload) {
        // 确保必要的字段
        const data = {
            ProductId: CONFIG.PRODUCT.ID,
            ...payload
        };

        return await this.call(CONFIG.ENDPOINTS.CALCULATE, 'POST', data);
    }

    /**
     * 保存提案
     */
    async saveProposal(payload) {
        return await this.call(CONFIG.ENDPOINTS.SAVE_PROPOSAL, 'POST', payload);
    }

    /**
     * 绑定提案
     */
    async bindProposal(proposalNo) {
        return await this.call(CONFIG.ENDPOINTS.BIND_PROPOSAL, 'POST', {
            ProposalNo: proposalNo
        });
    }

    /**
     * 支付回调
     */
    async paymentCallback(proposalNo, paymentStatus = 'SUCCESS', paymentReference = '') {
        return await this.call(CONFIG.ENDPOINTS.PAYMENT_CALLBACK, 'POST', {
            ProposalNo: proposalNo,
            PaymentStatus: paymentStatus,
            PaymentReference: paymentReference || `PAY${Date.now()}`
        });
    }

    /**
     * 获取保单信息
     */
    async getPolicy(proposalNo) {
        return await this.call(`${CONFIG.ENDPOINTS.POLICY}?proposalNo=${proposalNo}`);
    }
}

// 创建全局 API 实例
const api = new InsureMOAPI();
