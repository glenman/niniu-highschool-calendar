/**
 * 全球旅行险投保平台 - 主应用逻辑
 */

// 全局状态
let appState = {
    currentStep: 1,
    formData: {},
    selectedPlan: null,
    calculationResult: null,
    proposalNo: null,
    policyNo: null
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    // 设置默认日期
    setDefaultDates();

    // 绑定表单提交事件
    const form = document.getElementById('insuranceForm');
    form.addEventListener('submit', handleFormSubmit);

    // 实时校验
    setupFormValidation();

    console.log('✅ 应用初始化完成');
}

/**
 * 设置默认日期
 */
function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const nextWeek = new Date(tomorrow);
    nextWeek.setDate(nextWeek.getDate() + 7);

    document.getElementById('effectiveDate').value = formatDate(tomorrow);
    document.getElementById('expiryDate').value = formatDate(nextWeek);

    // 自动计算年龄
    document.getElementById('dateOfBirth').addEventListener('change', (e) => {
        const birthDate = new Date(e.target.value);
        const age = calculateAge(birthDate);
        document.getElementById('insuredAge').value = age;
    });
}

/**
 * 格式化日期为 YYYY-MM-DD
 */
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

/**
 * 计算年龄
 */
function calculateAge(birthDate) {
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    return age;
}

/**
 * 设置表单校验
 */
function setupFormValidation() {
    const inputs = document.querySelectorAll('input[required], select[required]');

    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateField(input);
            }
        });
    });
}

/**
 * 校验单个字段
 */
function validateField(field) {
    const value = field.value.trim();
    const errorSpan = field.parentElement.querySelector('.error-message');

    // 清除错误状态
    field.classList.remove('error');
    errorSpan.classList.remove('show');
    errorSpan.textContent = '';

    // 必填校验
    if (field.required && !value) {
        showFieldError(field, errorSpan, '此字段为必填项');
        return false;
    }

    // 特定字段校验
    if (value) {
        switch (field.id) {
            case 'email':
                if (!isValidEmail(value)) {
                    showFieldError(field, errorSpan, '请输入有效的邮箱地址');
                    return false;
                }
                break;

            case 'mobile':
                if (!isValidPhone(value)) {
                    showFieldError(field, errorSpan, '请输入有效的手机号码');
                    return false;
                }
                break;

            case 'effectiveDate':
            case 'expiryDate':
                if (!isValidDateRange()) {
                    showFieldError(field, errorSpan, '失效日期必须晚于生效日期');
                    return false;
                }
                break;

            case 'insuredAge':
                const age = parseInt(value);
                if (age < 0 || age > 100) {
                    showFieldError(field, errorSpan, '年龄必须在 0-100 之间');
                    return false;
                }
                break;
        }
    }

    return true;
}

/**
 * 显示字段错误
 */
function showFieldError(field, errorSpan, message) {
    field.classList.add('error');
    errorSpan.textContent = message;
    errorSpan.classList.add('show');
}

/**
 * 邮箱校验
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * 手机号校验
 */
function isValidPhone(phone) {
    const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    return re.test(phone);
}

/**
 * 日期范围校验
 */
function isValidDateRange() {
    const effectiveDate = document.getElementById('effectiveDate').value;
    const expiryDate = document.getElementById('expiryDate').value;

    if (!effectiveDate || !expiryDate) return true;

    return new Date(expiryDate) > new Date(effectiveDate);
}

/**
 * 表单提交处理
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    // 校验所有必填字段
    const form = e.target;
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    if (!isValid) {
        showError('请填写所有必填项');
        return;
    }

    // 收集表单数据
    collectFormData();

    // 进入下一步
    goToStep(2);
    await loadPlans();
}

/**
 * 收集表单数据
 */
function collectFormData() {
    const form = document.getElementById('insuranceForm');
    const formData = new FormData(form);

    appState.formData = {
        EffectiveDate: formData.get('EffectiveDate'),
        ExpiryDate: formData.get('ExpiryDate'),
        TravelType: parseInt(formData.get('TravelType')),
        TripType: parseInt(formData.get('TripType')),
        TravelPolicyType: CONFIG.DEFAULTS.TRAVEL_POLICY_TYPE,
        Customer: {
            Name: formData.get('Customer.Name'),
            Gender: formData.get('Customer.Gender'),
            DateOfBirth: formData.get('Customer.DateOfBirth'),
            Email: formData.get('Customer.Email'),
            Mobile: formData.get('Customer.Mobile'),
            IdNo: formData.get('Customer.IdNo'),
            IdType: formData.get('Customer.IdType')
        },
        Travelers: [
            {
                Name: formData.get('Customer.Name'),
                InsuredAge: parseInt(formData.get('Travelers[0].InsuredAge')),
                Gender: formData.get('Customer.Gender')
            }
        ]
    };

    console.log('📝 表单数据:', appState.formData);
}

/**
 * 加载产品方案
 */
async function loadPlans() {
    showLoading(true);

    try {
        console.log('🚀 开始加载产品方案...');
        console.log('📦 Product ID:', CONFIG.PRODUCT.ID);
        console.log('🌐 Base URL:', CONFIG.BASE_URL);
        
        const result = await api.getPlanList(CONFIG.PRODUCT.ID);
        
        console.log('✅ 方案数据:', result);
        
        if (!result || !result.Plans || result.Plans.length === 0) {
            throw new Error('未找到可用的保障方案');
        }

        renderPlans(result.Plans);
        showSuccess(`成功加载 ${result.Plans.length} 个保障方案`);
        
        console.log('✅ 方案渲染完成');
    } catch (error) {
        console.error('❌ 加载方案失败:', error);
        console.error('Stack:', error.stack);
        
        let errorMessage = '加载方案失败';
        
        if (error.message.includes('网络连接失败')) {
            errorMessage = '无法连接到服务器，请检查网络连接';
        } else if (error.message.includes('CORS')) {
            errorMessage = '跨域请求被阻止，请访问 <a href="debug.html" target="_blank">调试页面</a> 检查连接';
        } else if (error.message.includes('HTTP 401') || error.message.includes('HTTP 403')) {
            errorMessage = '认证失败，请检查 Auth Token 是否有效';
        } else {
            errorMessage = `加载失败: ${error.message}`;
        }
        
        showError(errorMessage);
        
        // 显示错误提示和调试链接
        const container = document.getElementById('plansContainer');
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: var(--error-color);">无法加载保障方案</h3>
                <p style="color: var(--text-secondary); margin: 1rem 0;">
                    ${error.message}
                </p>
                <div style="background: var(--background); padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: left; font-family: monospace; font-size: 0.875rem;">
                    <strong>调试信息：</strong><br>
                    • Product ID: ${CONFIG.PRODUCT.ID}<br>
                    • API URL: ${CONFIG.BASE_URL}<br>
                    • 错误: ${error.message}<br>
                    <br>
                    请打开浏览器控制台 (F12) 查看详细日志
                </div>
                <p style="color: var(--text-secondary); margin: 1rem 0; font-size: 0.875rem;">
                    访问 <a href="debug.html" target="_blank" style="color: var(--primary-color);">调试页面</a> 
                    进行详细测试
                </p>
                <button class="btn-primary" onclick="loadPlans()" style="margin-top: 1rem;">
                    🔄 重新加载
                </button>
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

/**
 * 渲染方案卡片
 */
function renderPlans(plans) {
    console.log('🎨 开始渲染方案，数量:', plans.length);
    
    const container = document.getElementById('plansContainer');
    
    if (!container) {
        console.error('❌ 找不到 plansContainer 元素');
        return;
    }
    
    container.innerHTML = '';

    plans.forEach((plan, index) => {
        console.log(`📋 渲染方案 ${index + 1}: ${plan.PlanName}`);
        const card = createPlanCard(plan, index);
        container.appendChild(card);
    });
    
    console.log('✅ 方案渲染完成');
}

/**
 * 创建方案卡片
 */
function createPlanCard(plan, index) {
    const card = document.createElement('div');
    card.className = 'plan-card';
    card.dataset.planCode = plan.PlanCode;

    const coveragesHtml = plan.Coverages ? plan.Coverages.map(cov => `
        <div class="coverage-item">
            <span class="coverage-name">${cov.ElementName || cov.Code}</span>
            <span class="coverage-amount">${formatCurrency(cov.SumInsured)}</span>
        </div>
    `).join('') : '';

    card.innerHTML = `
        <div class="plan-name">${plan.PlanName}</div>
        <div class="plan-description">${plan.PlanDescription || '全面旅行保障'}</div>
        <div class="plan-price">
            ${formatCurrency(plan.Premium || 0)}
            <span>/ 人</span>
        </div>
        <div class="coverages">
            <h4>保障内容</h4>
            ${coveragesHtml}
        </div>
    `;

    card.addEventListener('click', () => selectPlan(plan, card));

    return card;
}

/**
 * 选择方案
 */
function selectPlan(plan, cardElement) {
    console.log('✅ 选择方案:', plan.PlanName);
    
    // 移除其他选中状态
    document.querySelectorAll('.plan-card').forEach(card => {
        card.classList.remove('selected');
    });

    // 添加选中状态
    cardElement.classList.add('selected');

    // 保存选中的方案
    appState.selectedPlan = plan;

    // 启用下一步按钮
    document.getElementById('btnStep2Next').disabled = false;
    
    console.log('✅ 方案已选择，可以点击下一步');
}

/**
 * 计算保费
 */
async function calculatePremium() {
    if (!appState.selectedPlan) {
        showError('请先选择一个方案');
        return;
    }

    showLoading(true);

    try {
        const payload = {
            ...appState.formData,
            PlanCode: appState.selectedPlan.PlanCode
        };

        const result = await api.calculatePremium(payload);
        appState.calculationResult = result;

        console.log('💰 保费计算结果:', result);

        // 进入下一步
        goToStep(3);
        renderQuotation(result);
    } catch (error) {
        showError('保费计算失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * 渲染报价摘要
 */
function renderQuotation(data) {
    const container = document.getElementById('quotationSummary');

    const html = `
        <h3>保险报价详情</h3>

        <div class="summary-row">
            <span class="summary-label">产品名称</span>
            <span class="summary-value">${data.PlanName}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">保障期间</span>
            <span class="summary-value">${data.EffectiveDate} 至 ${data.ExpiryDate}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">投保人</span>
            <span class="summary-value">${data.Customer.Name}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">旅行类型</span>
            <span class="summary-value">${getTravelTypeName(data.TravelType)}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">行程类型</span>
            <span class="summary-value">${getTripTypeName(data.TripType)}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">保费</span>
            <span class="summary-value">${formatCurrency(data.Premium, data.Currency)}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">税费</span>
            <span class="summary-value">${formatCurrency(data.Tax, data.Currency)}</span>
        </div>

        <div class="summary-row total">
            <span class="summary-label">应付总额</span>
            <span class="summary-value">${formatCurrency(data.TotalPremium, data.Currency)}</span>
        </div>

        <div class="coverages" style="margin-top: 2rem;">
            <h4>保障内容</h4>
            ${data.Coverages.map(cov => `
                <div class="coverage-item">
                    <span class="coverage-name">${cov.Name}</span>
                    <span class="coverage-amount">${formatCurrency(cov.SumInsured)}</span>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = html;
}

/**
 * 确认报价
 */
async function confirmQuotation() {
    showLoading(true);

    try {
        // 1. 保存提案
        const saveResult = await api.saveProposal(appState.calculationResult);
        appState.proposalNo = saveResult.ProposalNo;

        console.log('💾 提案已保存:', saveResult);

        // 2. 绑定提案
        const bindResult = await api.bindProposal(appState.proposalNo);
        console.log('🔗 提案已绑定:', bindResult);

        // 3. 进入支付步骤
        goToStep(4);
        renderPaymentInfo();

        showSuccess('报价已确认，请完成支付');
    } catch (error) {
        showError('确认报价失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * 渲染支付信息
 */
function renderPaymentInfo() {
    const container = document.getElementById('paymentAmount');
    const data = appState.calculationResult;

    container.innerHTML = `
        ${formatCurrency(data.TotalPremium, data.Currency)}
    `;
}

/**
 * 处理支付
 */
async function processPayment() {
    showLoading(true);

    try {
        // 模拟支付成功
        const paymentResult = await api.paymentCallback(
            appState.proposalNo,
            'SUCCESS',
            `PAY${Date.now()}`
        );

        appState.policyNo = paymentResult.PolicyNo;

        console.log('💳 支付成功，保单已签发:', paymentResult);

        // 进入完成步骤
        goToStep(5);
        renderPolicyDetails(paymentResult);

        showSuccess('支付成功，保单已签发！');
    } catch (error) {
        showError('支付失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * 渲染保单详情
 */
function renderPolicyDetails(data) {
    const container = document.getElementById('policyDetails');

    const html = `
        <div class="summary-row">
            <span class="summary-label">保单号码</span>
            <span class="summary-value">${data.PolicyNo}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">投保单号</span>
            <span class="summary-value">${data.ProposalNo}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">产品方案</span>
            <span class="summary-value">${data.PlanName}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">保障期间</span>
            <span class="summary-value">${data.EffectiveDate} 至 ${data.ExpiryDate}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">投保人</span>
            <span class="summary-value">${data.Customer.Name}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">保费</span>
            <span class="summary-value">${formatCurrency(data.TotalPremium, data.Currency)}</span>
        </div>

        <div class="summary-row">
            <span class="summary-label">保单状态</span>
            <span class="summary-value" style="color: var(--success-color);">已生效</span>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * 下载保单
 */
function downloadPolicy() {
    showSuccess('保单下载功能开发中...');
    // 实际项目中可以调用后端生成 PDF
}

/**
 * 开始新的投保
 */
function startNew() {
    // 重置状态
    appState = {
        currentStep: 1,
        formData: {},
        selectedPlan: null,
        calculationResult: null,
        proposalNo: null,
        policyNo: null
    };

    // 重置表单
    document.getElementById('insuranceForm').reset();
    setDefaultDates();

    // 返回第一步
    goToStep(1);
}

/**
 * 切换步骤
 */
function goToStep(stepNumber) {
    // 隐藏所有步骤
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });

    // 显示目标步骤
    document.getElementById(`step${stepNumber}`).classList.add('active');

    // 更新进度条
    updateProgressBar(stepNumber);

    appState.currentStep = stepNumber;

    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 更新进度条
 */
function updateProgressBar(stepNumber) {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNum = index + 1;

        if (stepNum < stepNumber) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (stepNum === stepNumber) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

/**
 * 格式化货币
 */
function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * 获取旅行类型名称
 */
function getTravelTypeName(type) {
    const types = {
        1: '单次旅行',
        2: '多次旅行'
    };
    return types[type] || '未知';
}

/**
 * 获取行程类型名称
 */
function getTripTypeName(type) {
    const types = {
        1: '商务',
        2: '休闲',
        3: '留学'
    };
    return types[type] || '未知';
}

/**
 * 显示 Loading
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

/**
 * 显示错误消息
 */
function showError(message) {
    showToast(message, 'error');
}

/**
 * 显示成功消息
 */
function showSuccess(message) {
    showToast(message, 'success');
}

/**
 * 显示 Toast 消息
 */
function showToast(message, type = 'error') {
    const toastId = type === 'error' ? 'errorToast' : 'successToast';
    const toast = document.getElementById(toastId);
    const messageSpan = toast.querySelector('.toast-message');

    messageSpan.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 绑定下一步按钮事件
document.getElementById('btnStep2Next').addEventListener('click', async () => {
    console.log('🖱️ 点击下一步按钮');
    if (!appState.selectedPlan) {
        showError('请先选择一个保障方案');
        return;
    }
    
    await calculatePremium();
});
