# 🔴 紧急调试步骤 - 如果仍然失败

## ⚠️ 立即操作（不要跳过）

### 步骤1: 打开开发者工具

**现在就按 F12 键！**

### 步骤2: 切换到 Console 标签

**查看是否有红色错误信息**

如果有，**立即截图**发给我，包括：
- 完整的错误信息
- 错误的文件名和行号
- 错误堆栈

### 步骤3: 切换到 Network 标签

1. 填写表单
2. 提交
3. 选择方案
4. 点击"计算保费"
5. 在Network中找到 `EUDemoTRVL01Calculate` 请求
6. 点击它
7. 切换到 `Payload` 标签
8. **复制完整的payload内容**

### 步骤4: 在Console中运行调试命令

复制粘贴以下命令到Console：

```javascript
// 检查ProductId
console.log('=== 调试信息 ===');
console.log('CONFIG.PRODUCT_ID:', CONFIG.PRODUCT_ID);
console.log('appState.productId:', appState.productId);
console.log('appState.formData:', appState.formData);
console.log('appState.selectedPlan:', appState.selectedPlan);
```

**把输出结果复制发给我**

---

## 🎯 我需要的信息

如果问题仍然存在，请提供：

### 1. Console错误截图
```
按 F12 → Console → 截图所有红色错误
```

### 2. Network Payload内容
```
按 F12 → Network → 找到Calculate请求 → Payload → 复制内容
```

### 3. 调试命令输出
```
复制上面调试命令的输出结果
```

### 4. 产品选择框截图
```
截取首页的产品选择框部分
```

---

## 💡 临时解决方案

如果上述步骤太复杂，**现在就试试这个**：

### 方案1: 无痕模式（最快）

```
Chrome: Ctrl + Shift + N
Firefox: Ctrl + Shift + P
Safari: Cmd + Shift + N
```

然后访问：
```
https://glenman.github.io/insuremo-demo/
```

### 方案2: 简化测试版

直接访问简化版本（没有缓存问题）：
```
https://glenman.github.io/insuremo-demo/simple-test.html
```

---

## 🔧 如果你是开发人员

在Console中运行这个完整测试：

```javascript
// 完整API测试
const testAPI = async () => {
    const BASE_URL = 'https://portal-gw.insuremo.com/platform/api-orchestration-test';
    const TOKEN = 'MOATbWg4aRISAep86MorzeBulKla18sq';
    
    // 测试Calculate API
    const payload = {
        ProductId: 375604942,
        ProductCode: 'TRVL01',
        PlanCode: 'TRVL0120200001',
        EffectiveDate: '2026-03-26',
        ExpiryDate: '2026-04-05',
        TravelType: 1,
        TripType: 1,
        TravelPolicyType: 'INDI',
        Customer: {
            Name: 'Test',
            Gender: 'M',
            DateOfBirth: '1990-01-01'
        },
        Travelers: [{
            Name: 'Test',
            InsuredAge: 30,
            Gender: 'M'
        }]
    };
    
    console.log('📤 发送payload:', payload);
    
    const response = await fetch(`${BASE_URL}/v1/flow/EUDemoTRVL01Calculate`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    console.log('✅ API响应:', result);
    
    if (result.Success) {
        console.log('🎉 API调用成功！保费:', result.Data.TotalPremium, result.Data.Currency);
    } else {
        console.log('❌ API调用失败:', result.Error || result);
    }
};

testAPI();
```

---

## 📞 联系我

如果问题持续，**立即提供以下信息**：

1. ✅ Console错误截图
2. ✅ Network Payload内容
3. ✅ 调试命令输出
4. ✅ 产品选择框截图

**我会立即帮你解决！**

---

**紧急程度**: 🔴 高  
**需要信息**: 上述4项  
**响应时间**: 立即
