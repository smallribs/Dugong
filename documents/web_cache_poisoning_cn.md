# Web Cache Poisoning RAG 知识库

## 概述

Web Cache Poisoning（Web 缓存投毒）是一类利用缓存系统与后端应用对请求理解不一致而产生的漏洞。

攻击者通过构造特殊请求，让缓存服务器保存包含恶意内容的响应，随后其他用户访问相同资源时会命中被污染的缓存。

这类漏洞常见于：

- CDN
- Reverse Proxy
- HTTP Cache
- Framework Cache
- Edge Cache

影响范围通常远大于普通 XSS。

---

# 核心思想

缓存系统认为：

A请求 == B请求

但应用服务器认为：

A请求 != B请求

于是：

- 缓存复用了错误响应
- 恶意内容被缓存
- 所有用户都会获得恶意响应

---

# 基础概念

## Cache Key（缓存键）

缓存服务器通常不会完整比较整个 HTTP 请求。

一般只会使用部分字段构建缓存键，例如：

- URL
- Path
- Query
- Host
- Method

示例：

GET /index
Host: example.com

如果两个请求的 Cache Key 相同，则缓存系统认为它们是同一个请求。

---

## Unkeyed Input（未参与缓存键的输入）

某些 HTTP Header 或参数：

- 会被后端处理
- 但不会参与 Cache Key 计算

这些字段被称为：

Unkeyed Input

典型 Header：

- X-Forwarded-Host
- X-Original-URL
- X-Rewrite-URL
- X-Forwarded-Scheme
- User-Agent
- Referer
- Cookie
- Host Override

如果后端会使用这些字段生成响应，就可能导致缓存投毒。

---

# 经典攻击流程

## Step 1：寻找 Unkeyed Input

测试哪些 Header：

- 能影响响应
- 不参与缓存键

常用方法：

- 修改 Header
- 对比响应
- 观察缓存命中情况

---

## Step 2：让后端生成恶意响应

目标：

让服务器输出攻击者控制的数据。

常见目标：

- HTML 注入
- JavaScript 注入
- Open Redirect
- Header Injection
- CSS 注入
- JSON 污染

---

## Step 3：让缓存保存恶意响应

观察缓存相关 Header：

- Cache-Control
- Age
- X-Cache
- CF-Cache-Status
- X-Served-By
- Via

如果响应被缓存，则后续用户都会获得恶意内容。

---

# 经典案例

攻击请求：

GET /
Host: victim.com
X-Forwarded-Host: evil.com

后端生成：

<script src="https://evil.com/app.js"></script>

CDN 缓存该页面。

后续正常用户访问：

GET /
Host: victim.com

获得：

<script src="https://evil.com/app.js"></script>

结果：

Persistent XSS

---

# 常见攻击类型

## 1. Persistent XSS

最常见。

攻击者让缓存保存恶意 JS。

所有用户都会执行。

---

## 2. Open Redirect

缓存恶意跳转页面。

用于：

- 钓鱼
- OAuth 劫持
- Token Theft

---

## 3. Cache Deception

诱导缓存保存敏感内容。

例如：

- 用户信息
- API 返回
- Dashboard 页面

---

## 4. CPDoS（Cache Poisoned Denial of Service）

让缓存保存错误页面：

- 400
- 403
- 404
- 500

导致所有用户无法访问。

---

## 5. JavaScript Resource Poisoning

污染 JS 文件缓存。

影响通常比 HTML 更严重。

---

# 高危 Header

高频危险 Header：

- X-Forwarded-Host
- X-Forwarded-Proto
- X-Original-URL
- X-Rewrite-URL
- Forwarded
- X-Host
- X-HTTP-Host-Override
- X-Forwarded-Scheme
- X-Forwarded-Port

---

# 常见缓存系统

## CDN

- Cloudflare
- Fastly
- Akamai
- CloudFront

## Reverse Proxy

- Nginx
- Varnish
- HAProxy
- Apache Traffic Server

## Framework Cache

- Next.js
- Nuxt
- Django cache
- Rails cache

---

# 常见危险行为

## 1. Host Header Reflection

后端将 Host Header 输出到页面。

例如：

<script src="https://HOST/app.js"></script>

---

## 2. Protocol Reflection

根据 X-Forwarded-Proto 输出：

http://
https://

可能导致 Mixed Content 或 JS 注入。

---

## 3. URL Rewriting

后端信任：

- X-Original-URL
- X-Rewrite-URL

可能导致路径混淆。

---

# 缓存相关 Header

## Cache-Control

控制缓存策略。

示例：

Cache-Control: public, max-age=3600

---

## Age

表示缓存已存在时间。

示例：

Age: 120

---

## X-Cache

常见值：

- HIT
- MISS
- BYPASS

---

## CF-Cache-Status

Cloudflare 特有 Header。

常见值：

- HIT
- MISS
- DYNAMIC
- EXPIRED

---

# 判断缓存是否命中

常见方法：

- 多次请求
- 观察 Age 增长
- X-Cache: HIT
- 响应时间变短

---

# Burp Suite 测试技巧

## Repeater

手动测试 Header。

---

## Comparer

比较不同响应。

---

## Param Miner

PortSwigger 插件。

用于发现：

- 隐藏 Header
- Unkeyed Input
- 未公开参数

---

# Param Miner

作者：

James Kettle

功能：

- 自动枚举 Header
- 自动检测缓存键差异
- 自动发现隐藏参数

Web Cache Poisoning 研究中非常重要。

---

# Web Cache Entanglement

高级缓存攻击。

核心思想：

不同层：

- CDN
- Proxy
- Framework
- Backend

对 URL 的解析不同。

可能导致：

- Cache Key Confusion
- 路径穿越
- 规则绕过

---

# Cache Key Confusion

核心问题：

不同系统对“同一个请求”理解不同。

例如：

CDN：

/index

后端：

/index?admin=true

或者：

/index%2f

被不同层解析为不同路径。

---

# 与 Request Smuggling 的关系

两者本质类似：

都是：

不同层之间解释不一致。

Request Smuggling：

HTTP 边界不一致。

Cache Poisoning：

缓存键理解不一致。

---

# 常见利用目标

## 1. CDN

最危险。

因为影响全球用户。

---

## 2. API Gateway

可能污染 API 响应。

---

## 3. SSR Framework

例如：

- Next.js
- Nuxt

常见缓存逻辑复杂。

---

# 防御方法

## 1. 所有输入参与 Cache Key

不要让：

- 后端使用
- 缓存忽略

的字段存在。

---

## 2. 禁止反射危险 Header

不要信任：

- X-Forwarded-Host
- Host
- X-Original-URL

---

## 3. 对动态页面禁用缓存

例如：

Cache-Control: no-store

---

## 4. 标准化 URL

统一：

- 编码
- Path
- Slash
- Query

避免解析差异。

---

## 5. 分层安全测试

同时测试：

- CDN
- Proxy
- Backend

不要只测试应用层。

---

# 关键研究文章

## 1. Web Cache Poisoning

PortSwigger 官方基础教程。

---

## 2. Practical Web Cache Poisoning

James Kettle 经典研究。

包含大量真实案例。

---

## 3. Web Cache Entanglement

高级缓存攻击研究。

重点研究：

- URL parser mismatch
- Cache key confusion
- CDN 行为差异

---

# 核心安全思想

现代 Web 安全中：

不同层之间的“解释不一致”是很多漏洞的根源。

包括：

- Request Smuggling
- Cache Poisoning
- Host Header Injection
- Path Confusion
- HTTP Desync
- CDN Mismatch

核心都是：

不同组件对同一请求理解不同。

---

# RAG 检索关键词

Web Cache Poisoning
Cache Key
Unkeyed Input
CDN Cache
Edge Cache
Persistent XSS
CPDoS
Cache Deception
X-Forwarded-Host
Host Header Injection
Cache-Control
CF-Cache-Status
X-Cache
Age Header
Cache Key Confusion
Web Cache Entanglement
Request Smuggling
HTTP Desync
Param Miner
James Kettle
PortSwigger

