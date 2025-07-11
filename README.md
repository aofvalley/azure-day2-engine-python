
# 🧾 Azure Day 2 Engine

## 🎯 Purpose

Create a modular, extensible platform to perform governed Azure operations (e.g. starting/stopping clusters, upgrade/backup databases, etc...) exposed securely and interactively through Azure API Management also adding AI capabilities with the new **MCP server preview**. This enables rich, role-aware service automation and seamless integration with IDPs, Generative AI agents and third party components.

---

## 🧠 Solution Architecture

| Layer | Components |
|-------|------------|
| **API Runtime** | Azure Functions (.NET Isolated) per service |
| **Operations** | Implemented via `IResourceOperation` |
| **Discovery & Metadata** | Swagger (`/swagger.json`) generated dynamically |
| **Security** | RBAC enforcement via Azure AD claims |
| **API Gateway** | Azure API Management, exposing the APIs | 
| **MCP Gateway** | Azure API Management MCP server, exposing the APIs as MCP tools |

---

## 🔌 Key Capabilities

- ✅ **Custom Azure resource management and operations** via standardized APIs
- 🧩 **Pluggable operations** using DI in isolated Functions
- 🔐 **RBAC-enforced** via Azure AD roles like `AKS-Operator`, `PostgreSQL-Operator`
- 📜 **Governance** APp Insights for audit, metrics and APIM policies for throttling
- 📘 **OpenAPI generation** easy API discovery
- 🛠️ **API Gateway** using APIM's configuration
- 🛠️ **Preview MCP support** using APIM's configuration

---

## 🧠 Why This Matters

- 🛡️ Governance is enforced
- 🧰 Developers use standard tooling to automate tasks
- 🔌 Easily extensible to other Azure Services.
- 🧠 AI agents can discover and invoke operations semantically

---

## 📜 Project Tree

``` bash
AzureDay2Engine/
├── Program.cs
├── GlobalUsings.css
├── Interfaces/
│   └── IResourceOperation.cs
├── Operations/
│   └── StartAksClusterOperation.cs
├── Decorators/
│   ├── AuditDecorator.cs
│   ├── ThrottleDecorator.cs
│   └── MetricsDecorator.cs
├── Services/
│   ├── OperationRegistry.cs
│   └── SwaggerGenerator.cs
├── Functions/
│   ├── ExecuteOperation.cs
│   └── SwaggerEndpoint.cs
```