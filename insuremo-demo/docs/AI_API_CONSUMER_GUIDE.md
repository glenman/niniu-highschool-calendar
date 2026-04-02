# AI Developer Guide: EUDemo P2C Business APIs

> **Target Audience**: AI Coding Agents, AI UI Builders, AI Code Generators
>
> **Last Updated**: 2026-03-17
>
> **Base URL**: `https://portal-gw.insuremo.com/platform/api-orchestration-test`
>
> **Version**: 2.4

***

<br />

## Token Fetch Logic

If the UI is hosting in InsureMO, you can get token from UI application session storage with key: Authorization, you should pass the token into request header: Authorization, and please be aware of pre-check the token, it should be Bearer token.

## 🚀 Quick Start

### TRVL01 (Travel Insurance)

```bash
# 1. Get Products
GET /v1/flow/EUDemoProductList

# 2. Get Form Schema (use TRVL01 ProductId: 375604942)
GET /v1/flow/EUDemoPolicySchema?productId=375604942

# 3. Get Plans
GET /v1/flow/EUDemoPlanList?productId=375604942

# 4. Calculate Premium (PlanCode + TravelType + TripType REQUIRED)
POST /v1/flow/EUDemoTRVL01Calculate
{"ProductId": 375604942, "PlanCode": "TRVL0120200001", "EffectiveDate": "2026-03-16", "ExpiryDate": "2026-03-22", "TravelType": 2, "TripType": 2, "Travelers": [{"InsuredAge": 30, "Gender": "M", "Name": "John Smith"}]}

# 5. Save Proposal (use Calculate response)
POST /v1/flow/EUDemoTRVL01SaveProposal
{"ProductId": 375604942, "PlanCode": "TRVL0120200001", ...}
```

**Working Plans**: `TRVL0120200001` (Travel Classic) | **Required Fields**: `TravelType`, `TripType`

> **Full Flow**: Calculate → Save → Bind → Payment → Policy ✅ Verified Working

### HOME01 (Home Insurance)

```bash
# 1. Get Form Schema (use HOME01 ProductId: 536004405)
GET /v1/flow/EUDemoPolicySchema?productId=536004405

# 2. Get Plans
GET /v1/flow/EUDemoPlanList?productId=536004405

# 3. Calculate Premium (PlanCode + Property REQUIRED)
POST /v1/flow/EUDemoHOME01Calculate
{"ProductId": 536004405, "PlanCode": "CIFHOME20220001", "EffectiveDate": "2026-04-01", "Customer": {"Name": "John Smith"}, "Property": {"StreetName": "Main Street", "BlockNo": "123", "UnitNo": "A101", "City": "Chennai", "Country": "India", "BuildingType": "1"}}

# 4. Save Proposal (use Calculate response)
POST /v1/flow/EUDemoHOME01SaveProposal
{"ProductId": 536004405, "PlanCode": "CIFHOME20220001", ...}
```

**Working Plans**: `CIFHOME20220001` (Silver), `CIFHOME20220002` (Gold), `CIFHOME20220003` (Platinum)

**Property Fields**: `StreetName`, `BlockNo`, `UnitNo` | **Computed Address**: `StreetName, BlockNo, UnitNo`

> **Full Flow**: Calculate → Save → Bind → Payment → Policy ✅ Verified Working

***

## 📋 Tested Examples (Verified 2026-03-15)

### Calculate Example - TRVL0120200001

> **Important**: `TravelType` and `TripType` are REQUIRED for premium calculation.

**Request:**

```json
{
  "ProductId": 375604942,
  "PlanCode": "TRVL0120200001",
  "EffectiveDate": "2026-03-16",
  "ExpiryDate": "2026-03-22",
  "TravelPolicyType": "INDI",
  "TravelType": 2,
  "TripType": 2,
  "Customer": {
    "Name": "John Smith",
    "Email": "john.smith@example.com",
    "Mobile": "+1 555 123 4567",
    "DateOfBirth": "1996-03-15",
    "Gender": "M",
    "IdNo": "US12345678",
    "IdType": "3"
  },
  "Travelers": [
    {"InsuredAge": 30, "Gender": "M", "Name": "John Smith"}
  ]
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProductId": 375604942,
    "ProductCode": "TRVL01",
    "PlanCode": "TRVL0120200001",
    "PlanName": "Travel Classic",
    "EffectiveDate": "2026-03-16",
    "ExpiryDate": "2026-03-22",
    "TravelType": 2,
    "TripType": 2,
    "TravelPolicyType": "INDI",
    "Premium": 18,
    "Tax": 0,
    "TotalPremium": 18,
    "Currency": "EUR",
    "Customer": {
      "Name": "John Smith",
      "Email": "john.smith@example.com",
      "Mobile": "+1 555 123 4567",
      "DateOfBirth": "1996-03-15",
      "Gender": "M",
      "IdNo": "US12345678",
      "IdType": "3"
    },
    "Travelers": [
      {"Name": "John Smith", "Gender": "M", "DateOfBirth": "1996-01-01", "InsuredRelation": "1", "PassportNumber": ""}
    ],
    "Destinations": [
      {"SequenceNumber": 1}
    ],
    "Coverages": [
      {"Code": "PA01", "Name": "PA01", "SumInsured": 10000},
      {"Code": "TVLFDLY01", "Name": "TVLFDLY01", "SumInsured": 100},
      {"Code": "TVLBAG01", "Name": "TVLBAG01", "SumInsured": 1000},
      {"Code": "TVLTRCAN01", "Name": "TVLTRCAN01", "SumInsured": 1000}
    ]
  }
}
```

> **Note**:
>
> - `TravelType` and `TripType` are required for rate table lookup
> - `NationalityCode` in Travelers is ignored (removed from payload)
> - Calculate returns all request fields. Use the response directly for SaveProposal.

### SaveProposal Example - TRVL01GOLD

**Request:**

```json
{
  "ProductId": 375604942,
  "PlanCode": "TRVL01GOLD",
  "EffectiveDate": "2026-04-01",
  "ExpiryDate": "2026-04-15",
  "Premium": 16625,
  "Tax": 0,
  "TotalPremium": 16625,
  "Currency": "EUR",
  "Customer": {
    "Name": "Test Customer",
    "DateOfBirth": "1990-01-15",
    "Gender": "M",
    "Email": "test@example.com",
    "Mobile": "+1234567890"
  },
  "Travelers": [
    {"Name": "Traveler 1", "InsuredAge": 30, "Gender": "M"}
  ]
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProposalNo": "PTRVL010000000279",
    "Status": "QUOTATION",
    "ProductId": 375604942,
    "PlanCode": "TRVL01GOLD",
    "EffectiveDate": "2026-04-01",
    "ExpiryDate": "2026-04-15",
    "Premium": 16625,
    "Tax": 0,
    "TotalPremium": 16625,
    "Currency": "EUR",
    "Customer": {
      "Name": "Test Customer",
      "Gender": "M"
    },
    "Travelers": [
      {"Name": "Traveler 1", "Gender": "M"}
    ],
    "Coverages": [
      {"Code": "TVLMED01", "Name": "TVLMED01", "SumInsured": 750000}
    ]
  }
}
```

***

## 📋 HOME01 Examples (Verified 2026-03-17)

### Calculate Example - CIFHOME20220001 (Silver)

> **Important**: `PlanCode` and `Property` object are REQUIRED for premium calculation.

**Request:**

```json
{
  "ProductId": 536004405,
  "PlanCode": "CIFHOME20220001",
  "EffectiveDate": "2026-04-01",
  "Customer": {
    "Name": "Test Customer",
    "Email": "test@example.com",
    "Mobile": "+1234567890",
    "DateOfBirth": "1990-01-15",
    "Gender": "M"
  },
  "Property": {
    "StreetName": "Main Street",
    "BlockNo": "123",
    "UnitNo": "A101",
    "City": "Chennai",
    "State": "TamilNadu",
    "Country": "India",
    "BuildingName": "Test Building",
    "BuildingType": "1",
    "BuildDate": "2015-01-01"
  }
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProductId": 536004405,
    "ProductCode": "HOME01",
    "PlanCode": "CIFHOME20220001",
    "PlanName": "Silver",
    "EffectiveDate": "2026-04-01",
    "ExpiryDate": "2027-04-01",
    "Premium": 100,
    "Tax": 0,
    "TotalPremium": 100,
    "Currency": "EUR",
    "Customer": {
      "Name": "Test Customer",
      "Email": "test@example.com",
      "Mobile": "+1234567890",
      "DateOfBirth": "1990-01-15",
      "Gender": "M"
    },
    "Property": {
      "StreetName": "Main Street",
      "BlockNo": "123",
      "UnitNo": "A101",
      "Address": "Main Street, 123, A101",
      "City": "Chennai",
      "State": "TamilNadu",
      "Country": "India",
      "BuildingName": "Test Building",
      "BuildingType": "1",
      "BuildDate": "2015-01-01"
    },
    "Coverages": [
      {"Code": "BLPM0001", "Name": "Loss of Personal Money", "SumInsured": 500},
      {"Code": "CFHM001", "Name": "Contents Floater Home", "SumInsured": 50000},
      {"Code": "CFHMW001", "Name": "Contents Floater Home Worldwide", "SumInsured": 50000}
    ]
  }
}
```

### Full Flow Example - HOME01

**Step 1: Calculate**

```bash
POST /v1/flow/EUDemoHOME01Calculate
# Returns Premium: 100 EUR with Coverages array
```

**Step 2: SaveProposal** (use Calculate response)

```bash
POST /v1/flow/EUDemoHOME01SaveProposal
# Returns ProposalNo: PHOME010000000041, Status: QUOTATION
```

**Step 3: BindProposal**

```bash
POST /v1/flow/EUDemoHOME01BindProposal
{"ProposalNo": "PHOME010000000041"}
# Returns Status: BOUND
```

**Step 4: PaymentCallback**

```bash
POST /v1/flow/EUDemoHOME01PaymentCallback
{"ProposalNo": "PHOME010000000041", "PaymentStatus": "SUCCESS", "PaymentReference": "PAY123"}
# Returns PolicyNo: POHOME0100000020, Status: ISSUED
```

**Step 5: Policy**

```bash
GET /v1/flow/EUDemoHOME01Policy?proposalNo=PHOME010000000041
# Returns full policy details with Status: ISSUED
```

***

## Introduction for AI Agents

### What are P2C APIs?

P2C (Product to Channel) APIs are an **abstraction layer** over InsureMO's deeply nested Core Engine. They expose a **flattened, metadata-rich, and UI-friendly JSON format** that enables AI agents to:

1. **Understand product structure without insurance domain knowledge**
2. **Generate dynamic UI forms from schema metadata**
3. **Orchestrate the complete quote-and-buy journey**

As an AI UI Builder, you don't need to understand complex core engine insurance objects (Policy → Risk → Coverage → Benefit). You only need to:

- Parse the **Schema metadata**
- Dynamically render front-end forms
- Submit flattened payloads

### Key Design Principles

| Principle          | Description                                            |
| ------------------ | ------------------------------------------------------ |
| **Flattened**      | No nested hierarchies - simple arrays and objects      |
| **Metadata-Rich**  | Every field includes UI hints, validations, and labels |
| **UI-Friendly**    | Direct mapping to form components                      |
| **UpperCamelCase** | All JSON keys use PascalCase                           |

***

## 📊 Current API Status (2026-03-17)

### Overall Health: 92% Pass Rate | TRVL01 & HOME01 Full Flow Working ✅

| Category        | Status        | Notes                             |
| --------------- | ------------- | --------------------------------- |
| **Common APIs** | ✅ 5/6 Working | EUDemoCodeTableList has SDK issue |
| **TRVL01 APIs** | ✅ 5/5 Working | **Full flow verified working!**   |
| **HOME01 APIs** | ✅ 5/5 Working | **Full flow verified working!**   |

### Known Issues

| Issue                               | Impact                        | Status                  |
| ----------------------------------- | ----------------------------- | ----------------------- |
| TRVL01PLATINUM Calculate fails      | Cannot quote Platinum plan    | Open - SDK rating issue |
| ~~PaymentCallback INTERNAL\_ERROR~~ | ~~Cannot issue policies~~     | ✅ **RESOLVED**          |
| ~~HOME01 rating formula error~~     | ~~All HOME01 APIs blocked~~   | ✅ **RESOLVED**          |
| EUDemoCodeTableList INTERNAL\_ERROR | Cannot batch load code tables | Open - SDK issue        |

### Tested Plans (TRVL01)

| Plan Code      | Plan Name           | Calculate | SaveProposal | Premium    |
| -------------- | ------------------- | --------- | ------------ | ---------- |
| TRVL0120200001 | Travel Classic      | ✅         | ✅            | 13,300 USD |
| TRVL01GOLD     | Travel Gold Raj     | ✅         | ✅            | 16,625 USD |
| TRVL01PLATINUM | Travel Platinum Raj | ❌         | ✅            | N/A        |

### Tested Plans (HOME01)

| Plan Code       | Plan Name | Coverages | Calculate | Full Flow |
| --------------- | --------- | --------- | --------- | --------- |
| CIFHOME20220001 | Silver    | 17        | ✅         | ✅         |
| CIFHOME20220002 | Gold      | 17        | ✅         | ✅         |
| CIFHOME20220003 | Platinum  | 19        | ✅         | ✅         |

### Product IDs

| Product Code | Product ID | Status        |
| ------------ | ---------- | ------------- |
| TRVL01       | 375604942  | ✅ Recommended |
| HOME01       | 536004405  | ✅ Recommended |

***

## 🚨 Critical Rules for AI Agents

### Rule 1: NEVER Hardcode Form Fields

**WRONG:**

```javascript
// ❌ DO NOT DO THIS
<form>
  <input name="EffectiveDate" />
  <input name="ExpiryDate" />
  <select name="Gender">
    <option value="M">Male</option>
    <option value="F">Female</option>
  </select>
</form>
```

**CORRECT:**

```javascript
// ✅ Always fetch schema first
const schema = await fetchPolicySchema(productId);
const codeTables = await fetchCodeTableList(schema.CodeTableNames);

// Then dynamically generate form
<form>
  {schema.Fields.map(field => renderField(field, codeTables))}
</form>
```

### Rule 2: Naming Conventions

| Context              | Case             | Example                                           |
| -------------------- | ---------------- | ------------------------------------------------- |
| **JSON Body Keys**   | `UpperCamelCase` | `ProductId`, `PlanCode`, `EffectiveDate`          |
| **Query Parameters** | `lowerCamelCase` | `?productId=375604942`, `?proposalNo=POTRVL01...` |
| **Response Keys**    | `UpperCamelCase` | `Success`, `Data`, `ProposalNo`                   |

### Rule 3: HTTP Method Usage

| Method   | Purpose            | APIs                                                   |
| -------- | ------------------ | ------------------------------------------------------ |
| **GET**  | Retrieve data      | ProductList, PlanList, PolicySchema, CodeTable         |
| **POST** | Create/modify data | Calculate, SaveProposal, BindProposal, PaymentCallback |

### Rule 4: Batch Load Code Tables

Instead of calling `EUDemoCodeTable` multiple times, use `EUDemoCodeTableList` with the `CodeTableNames` array from the schema:

```javascript
// ✅ Efficient - one API call
const tables = await fetch('/v1/flow/EUDemoCodeTableList', {
  method: 'POST',
  body: JSON.stringify({ TableNames: schema.CodeTableNames })
});
```

***

## The 6-Step Orchestration Flow

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUOTE & BUY JOURNEY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: DISCOVERY                                                          │
│  ┌─────────────────────┐                                                    │
│  │ EUDemoProductList   │ → Get ProductId                                    │
│  └─────────────────────┘                                                    │
│           │                                                                 │
│           ▼                                                                 │
│  Step 2: UI GENERATION                                                      │
│  ┌─────────────────────┐    ┌──────────────────────┐                       │
│  │ EUDemoPolicySchema  │ +  │ EUDemoCodeTableList  │ → Build Form          │
│  └─────────────────────┘    └──────────────────────┘                       │
│           │                                                                 │
│           ▼                                                                 │
│  Step 3: PLAN SELECTION                                                     │
│  ┌─────────────────────┐                                                    │
│  │ EUDemoPlanList      │ → Show plan options                                │
│  └─────────────────────┘                                                    │
│           │                                                                 │
│           ▼                                                                 │
│  Step 4: QUOTING                                                            │
│  ┌─────────────────────────────┐                                            │
│  │ EUDemo{Product}Calculate    │ → Show premiums                            │
│  └─────────────────────────────┘                                            │
│           │                                                                 │
│           ▼                                                                 │
│  Step 5: PROPOSAL CREATION                                                  │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐        │
│  │ EUDemo{Product}SaveProposal │ →  │ EUDemo{Product}BindProposal │        │
│  └─────────────────────────────┘    └─────────────────────────────┘        │
│           │                                    │                            │
│           │                                    ▼                            │
│           │                              Status: BOUND                       │
│           │                                    │                            │
│           ▼                                    ▼                            │
│  Get ProposalNo                          Awaiting Payment                   │
│                                                                             │
│           ▼                                                                 │
│  Step 6: ISSUANCE                                                           │
│  ┌─────────────────────────────────┐                                        │
│  │ EUDemo{Product}PaymentCallback  │ → Get PolicyNo                        │
│  └─────────────────────────────────┘                                        │
│           │                                                                 │
│           ▼                                                                 │
│      Status: ISSUED                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

***

## Step-by-Step Guide

### Step 1: Discovery (EUDemoProductList)

**When to Call**: At the start of the journey, to show available products.

**Request:**

```
GET /v1/flow/EUDemoProductList
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "Products": [
      {
        "ProductCode": "TRVL01",
        "ProductId": 375604942,
        "ProductName": "Travel Insurance [BizOps Asset]"
      },
      {
        "ProductCode": "HOME01",
        "ProductId": 536004405,
        "ProductName": "Channel Integration Framework Home [BizOps Asset]"
      }
    ]
  }
}
```

**AI Action:**

- Extract `ProductId` for subsequent calls
- Render a product selector or catalog cards

***

### Step 2: UI Generation (EUDemoPolicySchema + EUDemoCodeTableList)

**When to Call**: After user selects a product, to generate the quotation form.

#### 2a. Fetch Policy Schema

**Request:**

```
GET /v1/flow/EUDemoPolicySchema?productId=375604942
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProductCode": "TRVL01",
    "ProductId": 375604942,
    "ProductName": "Travel Insurance [BizOps Asset]",
    "CodeTableNames": ["PolicyType", "Gender", "Country", "CurrencyCode", "YesNo"],
    "Fields": [
      {
        "ElementCode": "POLICY",
        "FieldName": "EffectiveDate",
        "Label": "Effective Date",
        "UiType": "date",
        "Required": true,
        "DataType": "date",
        "CodeTableName": null,
        "DefaultValue": null
      },
      {
        "ElementCode": "POLICY",
        "FieldName": "ExpiryDate",
        "Label": "Expiry Date",
        "UiType": "date",
        "Required": true,
        "DataType": "date",
        "CodeTableName": null,
        "DefaultValue": null
      },
      {
        "ElementCode": "R10007",
        "FieldName": "Gender",
        "Label": "Gender",
        "UiType": "select",
        "Required": true,
        "DataType": "string",
        "CodeTableName": "Gender",
        "DefaultValue": null
      },
      {
        "ElementCode": "R10007",
        "FieldName": "InsuredAge",
        "Label": "Age",
        "UiType": "text",
        "Required": true,
        "DataType": "number",
        "CodeTableName": null,
        "DefaultValue": null
      },
      {
        "ElementCode": "R10007",
        "FieldName": "Email",
        "Label": "Email Address",
        "UiType": "email",
        "Required": false,
        "DataType": "email",
        "CodeTableName": null,
        "DefaultValue": null
      },
      {
        "ElementCode": "R10007",
        "FieldName": "Mobile",
        "Label": "Mobile Number",
        "UiType": "tel",
        "Required": false,
        "DataType": "string",
        "CodeTableName": null,
        "DefaultValue": null
      }
    ]
  }
}
```

#### 2b. Fetch Code Tables (Batch)

**Request:**

```
POST /v1/flow/EUDemoCodeTableList
Content-Type: application/json

{
  "TableNames": ["Gender", "Country", "PolicyType"]
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "Gender": [
      { "Code": "M", "Name": "M" },
      { "Code": "F", "Name": "F" }
    ],
    "Country": [
      { "Code": "US", "Name": "United States" },
      { "Code": "GB", "Name": "United Kingdom" },
      { "Code": "CN", "Name": "China" },
      { "Code": "IN", "Name": "India" }
    ],
    "PolicyType": [
      { "Code": "INDIVIDUAL", "Name": "Individual" },
      { "Code": "GROUP", "Name": "Group" }
    ]
  }
}
```

**AI Action:**

- Store `CodeTableNames` array for batch loading
- Call `EUDemoCodeTableList` with all table names in one request
- Map each field's `CodeTableName` to the loaded code tables
- Generate form components based on `UiType` and `DataType`

***

### Step 3: Plan Selection (EUDemoPlanList)

**When to Call**: To show available plans/tiers for the selected product.

**Request:**

```
GET /v1/flow/EUDemoPlanList?productId=375604942
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProductId": 375604942,
    "ProductCode": "TRVL01",
    "ProductName": "Travel Insurance [BizOps Asset]",
    "ProductLine": "Travel",
    "ProductVersion": "1.0",
    "Description": "Travel insurance product for EU demo",
    "StartDate": "2025-01-01T00:00:00",
    "EndDate": "2030-12-31T00:00:00",
    "Plans": [
      {
        "PlanCode": "TRVL0120200001",
        "PlanName": "Travel Classic",
        "PlanDescription": "Basic travel coverage",
        "PlanEffectiveDate": "2020-01-01T00:00:00",
        "Coverages": [
          {
            "ElementCode": "TVLMED01",
            "ElementName": "Medical Care",
            "SumInsured": 50000,
            "Premium": 100,
            "Fields": [
              { "FieldName": "Deductible", "Value": "100" },
              { "FieldName": "PayDays", "Value": "30" }
            ]
          },
          {
            "ElementCode": "TVLBAG01",
            "ElementName": "Baggage",
            "SumInsured": 10000,
            "Premium": 50
          }
        ]
      },
      {
        "PlanCode": "TRVL01GOLD",
        "PlanName": "Travel Gold",
        "PlanDescription": "Premium travel coverage",
        "PlanEffectiveDate": "2025-12-05T00:00:00",
        "Coverages": [
          {
            "ElementCode": "TVLMED01",
            "ElementName": "Medical Care",
            "SumInsured": 100000,
            "Premium": 350
          }
        ]
      }
    ]
  }
}
```

**AI Action:**

- Display plans as selectable cards
- Show coverage details and SumInsured for each plan
- Save selected `PlanCode` for Calculate/SaveProposal

***

### Step 4: Quoting (EUDemo{Product}Calculate)

**When to Call**: After user fills the form, to calculate premiums.

**Request:**

```
POST /v1/flow/EUDemoTRVL01Calculate
Content-Type: application/json

{
  "ProductId": 375604942,
  "EffectiveDate": "2026-04-01",
  "ExpiryDate": "2026-04-10",
  "Travelers": [
    { "InsuredAge": 30, "Gender": "M", "Name": "John Doe" },
    { "InsuredAge": 28, "Gender": "F", "Name": "Jane Doe" }
  ],
  "Destinations": [
    {
      "TravelCountry": "India",
      "DestinationCountryCode": "India",
      "DestinationCityCode": "NewDelhi"
    }
  ]
}
```

**Minimum Request:**

```json
{
  "ProductId": 375604942,
  "EffectiveDate": "2026-04-01",
  "ExpiryDate": "2026-04-10",
  "Travelers": [
    { "InsuredAge": 30, "Gender": "M" }
  ]
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProductId": 375604942,
    "ProductCode": "TRVL01",
    "Plans": [
      {
        "PlanCode": "TRVL0120200001",
        "PlanName": "Travel Classic",
        "Premium": 13300,
        "Tax": 0,
        "TotalPremium": 13300,
        "Currency": "USD",
        "Coverages": [
          { "Code": "TVLMED01", "Name": "Medical Care", "SumInsured": 50000 },
          { "Code": "TVLBAG01", "Name": "Baggage", "SumInsured": 10000 },
          { "Code": "TVLFDLY01", "Name": "Flight Delay", "SumInsured": 500 }
        ]
      },
      {
        "PlanCode": "TRVL01GOLD",
        "PlanName": "Travel Gold Raj",
        "Premium": 35000,
        "Tax": 0,
        "TotalPremium": 35000,
        "Currency": "USD",
        "Coverages": [
          { "Code": "TVLMED01", "Name": "Medical Care", "SumInsured": 100000 }
        ]
      }
    ]
  }
}
```

**AI Action:**

- Display premium comparison for all plans
- Show coverage breakdown
- Let user select a plan

***

### Step 5: Proposal Creation

#### 5a. Save Proposal

**When to Call**: When user confirms their selection.

**Request:**

```
POST /v1/flow/EUDemoTRVL01SaveProposal
Content-Type: application/json

{
  "ProductId": 375604942,
  "PlanCode": "TRVL0120200001",
  "EffectiveDate": "2026-04-01",
  "ExpiryDate": "2026-04-10",
  "Customer": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Mobile": "+1234567890",
    "DateOfBirth": "1990-01-01",
    "Gender": "M"
  },
  "Travelers": [
    { "InsuredAge": 30, "Gender": "M", "Name": "John Doe" }
  ],
  "Destinations": [
    {
      "TravelCountry": "India",
      "DestinationCountryCode": "India",
      "DestinationCityCode": "NewDelhi"
    }
  ]
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProposalNo": "POTRVL0120260001",
    "Status": "QUOTATION",
    "EffectiveDate": "2026-04-01",
    "ExpiryDate": "2026-04-10",
    "Premium": 13300,
    "Tax": 0,
    "TotalPremium": 13300,
    "Currency": "USD",
    "PlanCode": "TRVL0120200001",
    "PlanName": "Travel Classic",
    "Customer": {
      "Name": "John Doe",
      "Email": "john@example.com",
      "Mobile": "+1234567890"
    },
    "Travelers": [
      { "Name": "John Doe", "Premium": 13300 }
    ],
    "Coverages": [
      { "Code": "TVLMED01", "Name": "Medical Care", "SumInsured": 50000 }
    ]
  }
}
```

**AI Action:**

- Extract `ProposalNo` - this is critical for subsequent calls
- Display quotation summary to user

#### 5b. Bind Proposal

**When to Call**: When user confirms to proceed with purchase.

**Request:**

```
POST /v1/flow/EUDemoTRVL01BindProposal
Content-Type: application/json

{
  "ProposalNo": "POTRVL0120260001"
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "ProposalNo": "POTRVL0120260001",
    "Status": "BOUND",
    "Message": "Proposal bound successfully. Awaiting payment.",
    "Premium": 13300,
    "Tax": 0,
    "TotalPremium": 13300,
    "Travelers": [...],
    "Coverages": [...]
  }
}
```

**AI Action:**

- Status is now `BOUND`
- Proceed to payment integration

***

### Step 6: Issuance (PaymentCallback)

**When to Call**: After successful payment.

**Request:**

```
POST /v1/flow/EUDemoTRVL01PaymentCallback
Content-Type: application/json

{
  "ProposalNo": "POTRVL0120260001",
  "PaymentStatus": "SUCCESS",
  "PaymentReference": "PAY123456"
}
```

**Response:**

```json
{
  "Success": true,
  "Data": {
    "PolicyNo": "PLTRVL0120260001",
    "ProposalNo": "POTRVL0120260001",
    "Status": "ISSUED",
    "Message": "Policy issued successfully",
    "PaymentReference": "PAY123456",
    "ProductCode": "TRVL01",
    "ProductId": 375604942,
    "PlanCode": "TRVL0120200001",
    "EffectiveDate": "2026-04-01",
    "ExpiryDate": "2026-04-10",
    "Premium": 13300,
    "Tax": 0,
    "TotalPremium": 13300,
    "Currency": "USD",
    "Customer": {
      "Name": "John Doe",
      "DateOfBirth": "1990-01-01",
      "Gender": "M",
      "Email": "john@example.com",
      "Mobile": "+1234567890"
    },
    "Travelers": [
      { "Name": "John Doe", "Premium": 13300 }
    ],
    "Coverages": [
      { "Code": "TVLMED01", "Name": "Medical Care", "SumInsured": 50000 }
    ]
  }
}
```

**AI Action:**

- Extract `PolicyNo`
- Display success confirmation page
- Status is now `ISSUED`

***

## Dynamic Form Generation

### Understanding PolicySchema Fields

| Field           | Description                               | Usage                                    |
| --------------- | ----------------------------------------- | ---------------------------------------- |
| `ElementCode`   | Group identifier (POLICY, R10007, LOC001) | Group fields visually                    |
| `FieldName`     | Unique field identifier                   | Use as input name                        |
| `Label`         | Display label                             | Show to user                             |
| `UiType`        | UI component type                         | `text`, `select`, `date`, `email`, `tel` |
| `Required`      | Validation flag                           | Mark as mandatory                        |
| `DataType`      | Data type                                 | `string`, `number`, `date`, `email`      |
| `CodeTableName` | Reference to code table                   | Load dropdown options                    |
| `DefaultValue`  | Default value for the field               | Pre-fill form inputs                     |
| `Validations`   | Validation rules                          | Apply Min, Max, Regex                    |

### UiType to Component Mapping

```javascript
function renderField(field, codeTables) {
  const { UiType, DataType, CodeTableName, Required, Label, FieldName, Validations, DefaultValue } = field;

  // Checkbox for boolean
  if (UiType === 'checkbox') {
    return <input type="checkbox" name={FieldName} required={Required} defaultChecked={DefaultValue} />;
  }

  // Select for dropdowns
  if (UiType === 'select') {
    const options = codeTables[CodeTableName] || [];
    return (
      <select name={FieldName} required={Required} defaultValue={DefaultValue}>
        <option value="">Select {Label}</option>
        {options.map(opt => (
          <option key={opt.Code} value={opt.Code}>{opt.Name}</option>
        ))}
      </select>
    );
  }

  // Date picker
  if (UiType === 'date' || DataType === 'date') {
    return <input type="date" name={FieldName} required={Required} defaultValue={DefaultValue} />;
  }

  // Email input
  if (UiType === 'email' || DataType === 'email') {
    return <input type="email" name={FieldName} required={Required} defaultValue={DefaultValue} />;
  }

  // Tel input
  if (UiType === 'tel') {
    return <input type="tel" name={FieldName} required={Required} defaultValue={DefaultValue} />;
  }

  // Number input
  if (DataType === 'number') {
    return (
      <input
        type="number"
        name={FieldName}
        required={Required}
        defaultValue={DefaultValue}
        min={Validations?.Min}
        max={Validations?.Max}
      />
    );
  }

  // Default text input
  return <input type="text" name={FieldName} required={Required} defaultValue={DefaultValue} />;
}
```

### Grouping Fields by ElementCode

```javascript
function groupFields(fields) {
  const groups = {
    POLICY: [],      // Policy-level fields (dates, type)
    R10007: [],      // Risk-level fields (traveler info)
    LOC001: []       // Location-level fields (destinations)
  };

  fields.forEach(field => {
    const group = groups[field.ElementCode] || groups.POLICY;
    group.push(field);
  });

  return groups;
}
```

***

## Status Workflow

### State Transitions

```
┌────────────┐     SaveProposal     ┌────────────┐
│   NEW      │ ──────────────────▶  │ QUOTATION  │
└────────────┘                      └────────────┘
                                         │
                                         │ BindProposal
                                         ▼
                                    ┌────────────┐
                                    │   BOUND    │
                                    └────────────┘
                                         │
                                         │ PaymentCallback (SUCCESS)
                                         ▼
                                    ┌────────────┐
                                    │  ISSUED    │
                                    └────────────┘
```

### Status Meanings

| Status      | Description                    | Next Action            |
| ----------- | ------------------------------ | ---------------------- |
| `QUOTATION` | Proposal saved, not confirmed  | Call `BindProposal`    |
| `BOUND`     | Quote locked, awaiting payment | Call `PaymentCallback` |
| `ISSUED`    | Policy active                  | Policy is valid        |
| `CANCELLED` | Policy cancelled               | No further action      |

***

## Request Payload Patterns

### TRVL01 Calculate/SavePayload Structure

```json
{
  "ProductId": 375604942,              // Required - from ProductList
  "PlanCode": "TRVL0120200001",        // Required for Save - from PlanList
  "EffectiveDate": "2026-04-01",       // Required - from form
  "ExpiryDate": "2026-04-10",          // Required - from form
  "Customer": {                        // Optional for Calculate, Required for Save
    "Name": "John Doe",
    "Email": "john@example.com",
    "Mobile": "+1234567890",
    "DateOfBirth": "1990-01-01",
    "Gender": "M"
  },
  "Travelers": [                       // Required - array of travelers
    {
      "InsuredAge": 30,                // Required
      "Gender": "M",                   // Required
      "Name": "John Doe",              // Optional
      "DateOfBirth": "1990-01-01",     // Optional
      "PassportNo": "AB123456"         // Optional
    }
  ],
  "Destinations": [                    // Optional
    {
      "TravelCountry": "India",
      "DestinationCountryCode": "India",
      "DestinationCityCode": "NewDelhi",
      "TravelFromCity": "Chennai",
      "DepartureDate": "2026-04-01",
      "FlightNumber": "DECCAN001"
    }
  ]
}
```

***

## Error Handling

### Error Response Format

```json
{
  "Success": false,
  "Error": {
    "Code": "VALIDATION_ERROR",
    "Message": "ProductId is required"
  }
}
```

### Common Error Codes

| Code                 | Description                   | Action                 |
| -------------------- | ----------------------------- | ---------------------- |
| `MISSING_PARAMETER`  | Required parameter missing    | Check request body     |
| `INVALID_PARAMETER`  | Parameter format invalid      | Validate input format  |
| `PRODUCT_NOT_FOUND`  | Product ID doesn't exist      | Verify ProductId       |
| `PROPOSAL_NOT_FOUND` | Proposal number doesn't exist | Verify ProposalNo      |
| `VALIDATION_ERROR`   | Business validation failed    | Check error message    |
| `CREATE_FAILED`      | Failed to create proposal     | Check data             |
| `BIND_FAILED`        | Failed to bind proposal       | Verify proposal status |
| `ISSUE_FAILED`       | Failed to issue policy        | Check payment status   |

### Error Handling Pattern

```javascript
async function callApi(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();

  if (!data.Success) {
    // Display error message to user
    showError(data.Error.Message);
    return null;
  }

  return data.Data;
}
```

***

## ⚠️ Data Continuity (Calculate → Save → Bind)

### Critical for AI Agents

When orchestrating multi-step API flows, **you must pass response data forward** to prevent data loss.

### Calculate → Save Flow

The Calculate API now returns ALL request fields. You can use the Calculate response directly as the Save request:

```javascript
// ✅ CORRECT - Use Calculate response for Save
const calcResult = await fetch('/v1/flow/EUDemoTRVL01Calculate', {
  method: 'POST',
  body: JSON.stringify({
    ProductId: 375604942,
    PlanCode: "TRVL01GOLD",
    EffectiveDate: "2026-04-01",
    ExpiryDate: "2026-04-10",
    Customer: { Name: "John Doe", Gender: "M" },
    Travelers: [{ Name: "John Doe", InsuredAge: 30, Gender: "M" }],
    Destinations: [{ CountryCode: "US" }]
  })
});

const calcData = await calcResult.json();

// Add PlanCode to the response and save
const savePayload = {
  ...calcData.Data,  // Contains all fields from Calculate
  PlanCode: "TRVL01GOLD"  // Ensure PlanCode is set
};

const saveResult = await fetch('/v1/flow/EUDemoTRVL01SaveProposal', {
  method: 'POST',
  body: JSON.stringify(savePayload)
});
```

### Fields Returned by Calculate

| Field            | Returned | Purpose                          |
| ---------------- | -------- | -------------------------------- |
| ProductId        | ✅        | Product identifier               |
| PlanCode         | ✅        | Selected plan                    |
| EffectiveDate    | ✅        | Coverage start date              |
| ExpiryDate       | ✅        | Coverage end date                |
| TravelType       | ✅        | Type of travel                   |
| TripType         | ✅        | Trip category                    |
| TravelPolicyType | ✅        | Policy type                      |
| Premium          | ✅        | Calculated premium               |
| Tax              | ✅        | Tax amount                       |
| TotalPremium     | ✅        | Total with tax                   |
| Currency         | ✅        | Currency code                    |
| Customer         | ✅        | Customer object (enriched)       |
| Travelers        | ✅        | Array of travelers (enriched)    |
| Destinations     | ✅        | Array of destinations (enriched) |
| Coverages        | ✅        | Coverage details                 |

### Fields Returned by SaveProposal

SaveProposal returns the same fields, plus:

- `ProposalNo` - Required for Bind/Payment
- `Status` - Current proposal status

***

## API Quick Reference

### Common APIs

| API              | Method | Path                              | Query/Body              | Purpose             |
| ---------------- | ------ | --------------------------------- | ----------------------- | ------------------- |
| ProductList      | GET    | `/v1/flow/EUDemoProductList`      | -                       | List products       |
| ProductStructure | GET    | `/v1/flow/EUDemoProductStructure` | `?productId={id}`       | Get elements        |
| PlanList         | GET    | `/v1/flow/EUDemoPlanList`         | `?productId={id}`       | Get plans           |
| PolicySchema     | GET    | `/v1/flow/EUDemoPolicySchema`     | `?productId={id}`       | Get form schema     |
| CodeTable        | GET    | `/v1/flow/EUDemoCodeTable`        | `?tableName={name}`     | Get single table    |
| CodeTableList    | POST   | `/v1/flow/EUDemoCodeTableList`    | `{"TableNames": [...]}` | Get multiple tables |

### Product APIs (TRVL01)

| API             | Method | Path                                   | Body                                                | Purpose          |
| --------------- | ------ | -------------------------------------- | --------------------------------------------------- | ---------------- |
| Calculate       | POST   | `/v1/flow/EUDemoTRVL01Calculate`       | Traveler data                                       | Get premiums     |
| SaveProposal    | POST   | `/v1/flow/EUDemoTRVL01SaveProposal`    | Full proposal                                       | Create quotation |
| BindProposal    | POST   | `/v1/flow/EUDemoTRVL01BindProposal`    | `{"ProposalNo": "..."}`                             | Lock quote       |
| PaymentCallback | POST   | `/v1/flow/EUDemoTRVL01PaymentCallback` | `{"ProposalNo": "...", "PaymentStatus": "SUCCESS"}` | Issue policy     |
| Policy          | GET    | `/v1/flow/EUDemoTRVL01Policy`          | `?proposalNo={no}`                                  | Get details      |

### Product APIs (HOME01)

| API             | Method | Path                                   | Body                                                | Purpose          |
| --------------- | ------ | -------------------------------------- | --------------------------------------------------- | ---------------- |
| Calculate       | POST   | `/v1/flow/EUDemoHOME01Calculate`       | Property data                                       | Get premiums     |
| SaveProposal    | POST   | `/v1/flow/EUDemoHOME01SaveProposal`    | Full proposal                                       | Create quotation |
| BindProposal    | POST   | `/v1/flow/EUDemoHOME01BindProposal`    | `{"ProposalNo": "..."}`                             | Lock quote       |
| PaymentCallback | POST   | `/v1/flow/EUDemoHOME01PaymentCallback` | `{"ProposalNo": "...", "PaymentStatus": "SUCCESS"}` | Issue policy     |
| Policy          | GET    | `/v1/flow/EUDemoHOME01Policy`          | `?proposalNo={no}`                                  | Get details      |

### Product IDs

| Product Code | Product ID | Product Name                       | Status                            |
| ------------ | ---------- | ---------------------------------- | --------------------------------- |
| TRVL01       | 375604942  | Travel Insurance \[BizOps Asset]   | ✅ **Recommended** - Fully Working |
| HOME01       | 536004405  | Channel Integration Framework Home | ✅ **Recommended** - Fully Working |

***

## Parallel API Calls Optimization

### Step 2 Optimization

Instead of sequential calls, load schema and code tables in parallel:

```javascript
// ✅ Efficient - parallel loading
async function loadFormData(productId) {
  // First, get schema to know which code tables are needed
  const schema = await fetch(`/v1/flow/EUDemoPolicySchema?productId=${productId}`);

  // Then load all code tables in one request
  const codeTables = await fetch('/v1/flow/EUDemoCodeTableList', {
    method: 'POST',
    body: JSON.stringify({ TableNames: schema.Data.CodeTableNames })
  });

  return { schema: schema.Data, codeTables: codeTables.Data };
}
```

### Step 4+5 Optimization

Load plan list while user is filling the form:

```javascript
// Preload plans in background
const planListPromise = fetch(`/v1/flow/EUDemoPlanList?productId=${productId}`);

// When user submits form
async function onSubmit(formData) {
  const planList = await planListPromise; // Already loaded
  const calculateResult = await fetch('/v1/flow/EUDemoTRVL01Calculate', {
    method: 'POST',
    body: JSON.stringify(formData)
  });
}
```

***

## Complete Example: Travel Insurance Quote Flow

### Pseudocode for AI Code Generation

```
1. On page load:
   - Call GET /v1/flow/EUDemoProductList
   - Display product cards (TRVL01 recommended)

2. On product select:
   - Call GET /v1/flow/EUDemoPolicySchema?productId=375604942
   - Extract CodeTableNames array
   - Call POST /v1/flow/EUDemoCodeTableList with CodeTableNames
   - Call GET /v1/flow/EUDemoPlanList?productId=375604942
   - Generate form from Fields array using UiType mapping
   - Pre-fill options for select fields from code tables

3. On form submit:
   - Build payload from form values (UpperCamelCase keys)
   - Call POST /v1/flow/EUDemoTRVL01Calculate
   - Display plan comparison with premiums

4. On plan select:
   - Call POST /v1/flow/EUDemoTRVL01SaveProposal with PlanCode
   - Extract ProposalNo from response
   - Display summary page

5. On confirm:
   - Call POST /v1/flow/EUDemoTRVL01BindProposal with ProposalNo
   - Redirect to payment

6. After payment success:
   - Call POST /v1/flow/EUDemoTRVL01PaymentCallback
   - Extract PolicyNo
   - Display success page with policy details
```

***

## Complete Example: Home Insurance Quote Flow

### Pseudocode for AI Code Generation

```
1. On page load:
   - Call GET /v1/flow/EUDemoProductList
   - Display product cards (HOME01 recommended)

2. On product select:
   - Call GET /v1/flow/EUDemoPolicySchema?productId=536004405
   - Extract CodeTableNames array (BuildingType, Country, etc.)
   - Call POST /v1/flow/EUDemoCodeTableList with CodeTableNames
   - Call GET /v1/flow/EUDemoPlanList?productId=536004405
   - Generate form from Fields array using UiType mapping
   - Pre-fill options for select fields from code tables (BuildingType is required)

3. On form submit:
   - Build payload from form values (UpperCamelCase keys)
   - Include Property object with StreetName, BlockNo, UnitNo, City, Country, BuildingType
   - Call POST /v1/flow/EUDemoHOME01Calculate
   - Display plan comparison with premiums

4. On plan select:
   - Call POST /v1/flow/EUDemoHOME01SaveProposal with PlanCode
   - Extract ProposalNo from response
   - Display summary page

5. On confirm:
   - Call POST /v1/flow/EUDemoHOME01BindProposal with ProposalNo
   - Redirect to payment

6. After payment success:
   - Call POST /v1/flow/EUDemoHOME01PaymentCallback
   - Extract PolicyNo
   - Display success page with policy details
```

***

## Data Models

### Customer Object

```json
{
  "Name": "John Doe",
  "DateOfBirth": "1990-01-01",
  "Gender": "M",
  "Email": "john@example.com",
  "Mobile": "+1234567890",
  "IdNo": "PASSPORT123",
  "IdType": "Passport"
}
```

### Traveler Object

```json
{
  "Name": "John Doe",
  "InsuredAge": 30,
  "Gender": "M",
  "DateOfBirth": "1990-01-01",
  "PassportNo": "AB123456"
}
```

### Destination Object

```json
{
  "TravelCountry": "India",
  "DestinationCountryCode": "India",
  "DestinationCityCode": "NewDelhi",
  "TravelFromCity": "Chennai",
  "DepartureDate": "2026-04-01",
  "FlightNumber": "DECCAN001"
}
```

### Coverage Object

```json
{
  "Code": "TVLMED01",
  "Name": "Medical Care",
  "SumInsured": 50000
}
```

### Property Object (HOME01)

**Input Fields:**

```json
{
  "StreetName": "Main Street",
  "BlockNo": "123",
  "UnitNo": "A101",
  "City": "Chennai",
  "State": "TamilNadu",
  "Country": "India",
  "BuildingName": "Sunrise Apartments",
  "BuildingType": "1",
  "BuildDate": "2015-01-01",
  "PostalCode": "600001"
}
```

**Response Fields (includes computed Address):**

```json
{
  "StreetName": "Main Street",
  "BlockNo": "123",
  "UnitNo": "A101",
  "Address": "Main Street, 123, A101",
  "City": "Chennai",
  "State": "TamilNadu",
  "Country": "India",
  "BuildingName": "Sunrise Apartments",
  "BuildingType": "1",
  "BuildDate": "2015-01-01",
  "PostalCode": "600001"
}
```

| Field          | Type   | Required | Description                                                          |
| -------------- | ------ | -------- | -------------------------------------------------------------------- |
| `StreetName`   | string | ❌        | Street name                                                          |
| `BlockNo`      | string | ❌        | Block/house number                                                   |
| `UnitNo`       | string | ❌        | Unit/apartment number                                                |
| `Address`      | string | ❌        | **Computed** - Format: `StreetName, BlockNo, UnitNo` (response only) |
| `City`         | string | ✅        | City name                                                            |
| `State`        | string | ❌        | State/province                                                       |
| `Country`      | string | ✅        | Country name                                                         |
| `BuildingName` | string | ❌        | Building name                                                        |
| `BuildingType` | string | ✅        | Building type code (from CodeTable)                                  |
| `BuildDate`    | date   | ❌        | Construction date (YYYY-MM-DD)                                       |
| `PostalCode`   | string | ❌        | Postal/ZIP code                                                      |

***

