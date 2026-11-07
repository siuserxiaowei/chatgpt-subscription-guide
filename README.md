# ChatGPT 订阅核对指南

这些页面使用简体中文。操作步骤都写成文字，不靠图片代替。

本仓库收录原创教程，帮助读者在购买或续费 ChatGPT 会员之前核对账号、账单渠道和原订单。它回答的是核对问题，不是商品广告。

这些教程以本仓库主分支上的文件为准。尚未合并进主分支的改动，还不是已发布版本。

## 这个仓库是做什么的

你可以用这里的教程做四件事。

分清 ChatGPT 会员和 API 额度。

在付款前确认当前登录的账号，以及是不是已经有订阅。

分别查看网页、Apple App Store 和 Google Play，避免两笔订阅同时存在。

付款后页面没有跳回，或账号状态没有变化时，先查原来的那一笔，而不是再付一次。

## 谁在维护

本仓库由 PayForGPT 编写并维护。PayForGPT 销售 ChatGPT 会员相关服务，本仓库和这家商家有商业关联。

这不是 OpenAI 的官方文档。这也不是 GitHub 的官方文档。这不是独立的第三方测评。

本仓库不保证页面会被搜索引擎收录，不保证排名、权重或购买转化。

品牌与服务说明见 [PayForGPT 网站首页](https://payforgpt.com/)。价格、库存和某一笔订单的交付条件，以你打开主站时的页面和该笔订单为准。本仓库不另列价格表。

## 适合谁看

准备购买 ChatGPT 会员，或已经扣款但不确定买到了什么的人。

同时使用网页和手机应用，担心重复订阅的人。

需要区分「对话会员」和「API 调用额度」的人。

如果你的问题是工作区管理员权限、企业合同或发票主体，这里只提醒你它和普通个人订阅不是同一条账单。具体权限以你的工作区设置和官方帮助页为准。

## 教程目录

下面每一项都是一篇已经放进本仓库的教程。

1. [会员付款和 API 额度不是同一笔账](docs/tutorials/01-membership-and-api-balance.md)
2. [付款前核对目标账号和已有订阅](docs/tutorials/02-check-account-before-paying.md)
3. [网页、App Store 和 Google Play 要分开查重](docs/tutorials/03-separate-web-apple-google.md)
4. [按需求区分 Plus 和 Pro，不要只看商品名](docs/tutorials/04-choose-plus-and-pro.md)
5. [付款后没有跳回时，先查原订单](docs/tutorials/05-check-original-order.md)
6. [求助前只收集脱敏信息](docs/tutorials/06-redact-before-asking-for-help.md)

写作和核实规则在另外两页。

[维护规范](docs/维护规范.md) 说明以后怎样改教程、哪些话不能写。

[事实核验记录](docs/事实核验记录.md) 记录外链在什么时候打开过、返回了什么状态、正文有没有读到。

检查命令写在 [怎样检查内部链接](#怎样检查内部链接)。脚本文件是 [内部链接检查脚本](scripts/check_internal_links.py)。

## 凭据不要发到公开处

不要把下面这些内容发到本仓库、聊天、邮件、订单备注或截图里。

ChatGPT 密码、邮箱密码、一次性验证码。

API token、access token、session、cookie。

PayForGPT 的查单密码、完整卡密。

完整银行卡号、完整支付凭证原图。

查单密码只填在 PayForGPT 订单查询页的密码框里。订单号可以在求助时提供。密码和订单号不是同一个东西。

怎样准备一份可以发出去的记录，见 [求助前只收集脱敏信息](docs/tutorials/06-redact-before-asking-for-help.md)。

## 官方订阅和商家订单不是同一件事

OpenAI 网页、Apple App Store 和 Google Play 上的订阅，由对应平台管理。在一个平台新买一笔，不会自动取消另一个平台上的旧订阅，也不会把旧订阅迁过来。

PayForGPT 的订单是商家订单。它使用订单号、下单邮箱和查单密码。它不是 chatgpt.com 结账页上的那一次官方订阅，也不是应用商店收据里的那一次订阅。

已经在某个平台扣过款时，先按 [付款后没有跳回时，先查原订单](docs/tutorials/05-check-original-order.md) 找到原来的记录。不要为了让状态刷新再付一笔。

## 本仓库不写这些内容

第二份价格表，或把某天看到的价格写成长期价格。

主站退款页以外的新退款承诺，或把主站口号改写成保证。

上传 token、密码、验证码或 session 的做法。

绕过平台地区限制、风控或使用限制的做法。

其他商家或其他站点的介绍。本仓库只讨论 PayForGPT 和 OpenAI 的官方订阅渠道。

## 怎样检查内部链接

在仓库根目录运行：

```bash
python3 scripts/check_internal_links.py --self-test
python3 scripts/check_internal_links.py --list-external
```

第一行检查脚本自己的样例。第二行检查本仓库的相对链接和标题锚点。

脚本不打开外部网址。终端里出现「通过」，只表示内部链接和锚点可用。外部页面是否有效，以 [事实核验记录](docs/事实核验记录.md) 为准。
