# Solution: Interactive CI/CD Deployment Pipeline with Public Trigger

This project demonstrates an unauthenticated, rate-limited public trigger for an AWS CodePipeline, enabling secure, auditable deployments via API Gateway and Lambda. It simulates a real-world scenario where public triggers are needed under strict quota enforcement and monitoring.

---

## 📌 Problem Statement

Enable unauthenticated external users to trigger an internal CI/CD pipeline securely, without risk of abuse. Traditional AWS CI/CD workflows are secured by IAM and kept private. This project explores how to safely expose a limited public entry point without compromising reliability, cost, or traceability.

---

## ⚙️ Architecture Overview

![Architecture](./screenshots/01-architecture.png)

---

## 🚀 Components

| Layer              | AWS Service           | Role                                             |
|-------------------|-----------------------|--------------------------------------------------|
| API Interface      | Amazon API Gateway    | Exposes public `/trigger` endpoint               |
| Rate Limiter       | AWS Lambda + DynamoDB | Enforces 3 requests per IP per 7-day period      |
| Execution Handler  | AWS Lambda            | Triggers the CodePipeline execution              |
| Observability      | CloudWatch + SNS      | Logs traffic and sends alert on each trigger     |
| Audit & Quotas     | DynamoDB TTL          | Enforces data expiry to manage weekly quotas     |

---

## 🛠️ Implementation Steps (Visual Evidence Included)

1. **API Gateway - /trigger Resource**  
   ![01](./screenshots/02-api-post.png)  
   *01 - The POST method configured under the /trigger resource.*

2. **Stage Deployment Confirmation**  
   ![02](./screenshots/03-stage-url.png)  
   *02 - API Gateway production stage deployed with invoke URL.*

3. **Lambda Handler – `PublicTriggerPipelineStart`**  
   ![03](./screenshots/04-lambda-code.png)  
   *03 - Python code enforces per-IP limits and triggers CodePipeline.*

4. **Lambda Trust Policy**  
   ![04](./screenshots/05-trust-policy.png)

5. **Inline Policies Applied**  
   ![05](./screenshots/06-inline-policies.png)

6. **InvokeTriggerPolicy**  
   ![06](./screenshots/07-invoke-policy.png)

7. **AllowDynamoDBUsagePolicy**  
   ![07](./screenshots/08-dynamodb-policy.png)

8. **PublishTriggerAlertPolicy**  
   ![08](./screenshots/09-sns-policy.png)

9. **CloudWatch Log – Successful Execution**  
   ![09](./screenshots/10-success-log.png)

10. **CloudWatch Log – Rate Limited**  
   ![10](./screenshots/11-ratelimit-log.png)

11. **DynamoDB Table Schema**  
   ![11](./screenshots/12-schema.png)

12. **TTL Attribute Enabled**  
   ![12](./screenshots/13-ttl-enabled.png)

13. **Sample Table Records with TTL**  
   ![13](./screenshots/14-item-view.png)

14. **SNS Topic Configuration**  
   ![14](./screenshots/15-sns-topic.png)

15. **Trigger Email Received**  
   ![15](./screenshots/16-sns-email.png)

16. **Trigger Execution - cURL Success**  
   ![16](./screenshots/17-curl-success.png)

17. **Trigger Denied - Rate Limit Hit**  
   ![17](./screenshots/18-curl-blocked.png)

---

## 🔐 Security Controls

- Lambda IAM role scoped to **3 purpose-specific inline policies**
- Per-IP **DynamoDB-based quota enforcement**
- **DynamoDB TTL** enforces 7-day expiry
- **SNS alert** on each trigger for auditability
- Full **CloudWatch logging** for trace and forensic review

---

## ✅ Well-Architected Framework Alignment

| Pillar               | Alignment                                                                 |
|----------------------|---------------------------------------------------------------------------|
| **Security**         | IAM least-privilege, request validation, alerting via SNS                 |
| **Reliability**      | Isolation of abusive actors, no shared state or race conditions           |
| **Operational Excellence** | Fully observable pipeline entry point with failure monitoring      |
| **Cost Optimization**| Serverless architecture, no idle resources, all Free Tier eligible        |
| **Performance Efficiency**| Sub-second Lambda execution, DynamoDB on-demand scaling             |

---

## 🧠 Architect Notes

### Error Handling Beyond Rate Limit

CodePipeline failures are caught and routed through SNS.  
To improve fault resilience, a Dead Letter Queue (DLQ) can be attached to the Lambda. In high-reliability environments, retry policies using EventBridge should also be considered.

---

### Rate Limiting Strategy Comparison

| Method                  | Pros                                         | Cons                                      |
|-------------------------|----------------------------------------------|-------------------------------------------|
| **DynamoDB TTL Logic**  | Tracks fine-grained quotas per IP, persistent | Requires custom logic and maintenance     |
| **API Gateway Throttling** | Built-in, easy setup                      | Cannot enforce per-IP quotas over time    |
| **AWS WAF**             | Global IP block patterns, flexible rules     | Lacks native quota tracking               |

This project uses DynamoDB to enforce “3 requests per IP per 7 days” — a business rule not directly supported by API Gateway or WAF.

---

### DynamoDB Scalability

DynamoDB is set to **on-demand** mode to auto-scale based on real usage. For high-volume traffic:
- Consider provisioned capacity + autoscaling
- Use SK prefixes to partition hot keys
- DynamoDB Accelerator (DAX) may reduce read latency

---

### Cost Notes

| Service         | Optimization |
|----------------|--------------|
| **Lambda**      | Free tier covers up to 1M invocations monthly |
| **API Gateway** | ~$3.50 per million calls, caching optional    |
| **DynamoDB**    | On-demand for low traffic, switchable to provisioned |
| **SNS**         | Email notifications negligible cost            |

This project is cost-effective for public-facing demos or controlled usage in dev environments.

---

## 🧩 Future Enhancements

- Infrastructure-as-Code (CDK or CloudFormation) for repeatable deployment
- DLQ integration with Lambda for retry resilience
- API Gateway usage plans or AWS WAF for perimeter throttling and abuse detection

---

## ✅ Result

The final system securely exposes a public-facing pipeline trigger. It combines Lambda-based execution, DynamoDB quota enforcement, and real-time alerting — all built using fully native AWS services and scoped under Free Tier.

---

**🔗 GitHub:** [github.com/oSedky](https://github.com/oSedky)  
**🌐 Portfolio:** [sedky.net](https://sedky.net)  
**📬 LinkedIn:** [www.linkedin.com/in/omarsedky](https://www.linkedin.com/in/omarsedky)