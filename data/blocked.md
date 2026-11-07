# 抓不到的厂商（记录原因，不编数字）

更新：2026-11-08 夜班

| 厂商 | 尝试的地址 | 结果 |
|---|---|---|
| Recharge | getrecharge.com/pricing | 返回 5KB 阻断页 |
| Skio | skio.com/pricing | 页面 500KB 但价格由脚本注入，HTML 无数字 |
| Appstle | appstle.com/pricing | 请求超时/无响应 |
| Bold Commerce | boldcommerce.com/pricing | 无响应 |
| Seal Subscriptions | sealsubscriptions.com/pricing | 页面有 HTML 但无价格文本 |
| Triple Whale | triplewhale.com/pricing | 返回 4.5KB 空壳 |
| AfterShip | aftership.com/pricing | 5.7KB 空壳 |
| Loop Returns | loopreturns.com/pricing | 341KB 但价格脚本注入 |
| Smile.io / LoyaltyLion | 各自 /pricing | 同上，无价格文本 |
| Tidio | tidio.com/pricing | 只抓到 $300/mo 一条，档位不全 |
| Lifetimely | lifetimely.io/pricing | 抓到 $49/$149/$499/$749/$999 与 $75 亚马逊加购，但 S/M/L 档位与订单量对应关系不完整，暂不收录 |

结论：订阅、物流、分析三类厂商普遍用 JS 渲染定价页。可行方法只剩两种：找它们的定价 API，或等它们把价格写进静态 HTML。三种方法里，"查帮助文档历史价格"这条本轮没试通，下轮继续。
