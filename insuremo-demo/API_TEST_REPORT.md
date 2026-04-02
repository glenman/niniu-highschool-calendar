# InsureMO API 测试报告

## 测试时间
2026-03-25 18:00 (Asia/Shanghai)

## 测试环境
- Base URL: https://portal-gw.insuremo.com/platform/api-orchestration-test
- Auth Token: Bearer MOATbWg4aRISAep86MorzeBulKla18sq
- Product: TRVL01 (Travel Insurance) - ProductId: 375604942

## 测试结果

### ✅ 1. 产品列表 (EUDemoProductList)
**状态**: 成功
**返回**: 3个产品（TRVL01, TRAVEL, HOME01）

### ✅ 2. Schema 获取 (EUDemoPolicySchema)
**状态**: 成功
**返回**: 25个表单字段定义

### ✅ 3. 方案列表 (EUDemoPlanList)
**状态**: 成功
**返回**: 3个方案（Travel Classic, Travel Gold Raj, Travel Platinum Raj）

### ✅ 4. 保费计算 (EUDemoTRVL01Calculate)
**状态**: 成功
**测试数据**:
- PlanCode: TRVL0120200001 (Travel Classic)
- 保险期间: 2026-03-16 至 2026-03-22 (7天)
- 保费: 18 EUR

**关键发现**:
- `TravelType` 和 `TripType` 是必填字段
- Customer 对象的完整信息有助于成功计算
- 返回的覆盖范围包括：PA01, TVLFDLY01, TVLBAG01, TVLTRCAN01

## 完整流程测试（待完成）
接下来需要测试：
- SaveProposal
- BindProposal
- PaymentCallback
- Policy

## 结论
✅ API 调用正常，可以进行前端开发
