import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const lessons = [
  {
    id:"web-engineering-01", title:"PostgreSQL、Alembic 与数据迁移", file:"01-postgresql-alembic-data-migration.md",
    cards:[
      ["postgres-result","overview-postgres-migration","v0.9 最后交付什么","PostgreSQL 迁移课做出什么","Web v0.9 把主存储迁到 PostgreSQL，并用迁移和导入校验保存数据语义。"],
      ["migration-version","concept-migration-contract","为什么结构版本要进代码","Alembic 版本表有什么用","数据库结构变化必须可排序、可复现、可审查，不能依赖手工改表。"],
      ["upgrade-head","concept-migration-contract","upgrade head 做什么","怎样推进到最新 revision","upgrade head 按 revision 链把数据库推进到当前代码要求的版本。"],
      ["migration-rollback","concept-migration-contract","迁移失败为什么要回滚","DDL 失败后怎样保持原结构","事务中的失败迁移应整体回滚，并在临时库修正后重试。"],
      ["import-idempotent","example-import-idempotent","SQLite 导入为什么能重复运行","教学数据导入怎样避免重复","导入依靠稳定业务键和唯一约束，使重复执行不增加记录或汇总。"],
      ["import-invariants","example-import-idempotent","迁移后核对哪些不变量","怎样证明数据迁移完整","核对记录数、小时汇总、主外键和幂等键，而不是只看脚本退出码。"],
      ["pool-pre-ping","overview-postgres-migration","连接池 pre ping 有什么用","数据库连接失效怎样被发现","pool_pre_ping 在借出连接前检查可用性，减少陈旧连接进入请求。"],
      ["run-v09","reproduce-dashboard-v09","怎样运行 v0.9 真实迁移测试","PostgreSQL 四项测试命令是什么","启动回环端口容器后运行 4 项真实 PostgreSQL 测试。"],
      ["modify-revision","modify-migration-column","怎样主动新增一个迁移列","新 revision 练习怎么做","先新增兼容列和测试，再升级、回填并验证旧数据仍可读取。"],
      ["revision-troubleshoot","troubleshoot-migration","找不到 Alembic revision 怎么排查","alembic_version 不一致怎么办","核对连接 URL、版本表和 revision 链，不直接改版本号掩盖问题。"],
      ["downgrade-boundary","troubleshoot-migration","为什么生产降级不能照搬教学 downgrade","downgrade base 的边界是什么","教学降级在临时库验证可逆性；生产数据回滚还要评估兼容与数据丢失。"],
      ["project-v09","project-dashboard-v09","v0.9 与 v0.8 的核心差异是什么","学习进度报告器迁移证据有哪些","v0.9 保留资源语义，新增 PostgreSQL、连接池、迁移版本和幂等导入证据。"]
    ]
  },
  {
    id:"web-engineering-02", title:"密码哈希、Cookie 会话与 CSRF 防护", file:"02-password-hashing-cookie-sessions-csrf.md",
    cards:[
      ["auth-result","overview-session-boundary","v0.10 最后交付什么","会话安全课做出什么","v0.10 增加 Argon2id、短期不透明会话、Cookie 身份与 CSRF 防护。"],
      ["argon2-hash","overview-session-boundary","为什么密码保存 Argon2id 哈希","密码能不能加密后保存","密码只保存专用慢哈希，验证时比较而不恢复原文。"],
      ["opaque-token","concept-cookie-session","为什么使用不透明会话令牌","为什么这课不自制 JWT","随机不透明值把会话状态留在服务端，便于到期和撤销。"],
      ["token-digest","concept-cookie-session","数据库为什么只存令牌摘要","会话原文落库有什么风险","请求携带原值，服务端用摘要查找；数据库泄露不能直接得到可用令牌。"],
      ["cookie-flags","concept-cookie-session","会话 Cookie 需要哪些属性","HttpOnly SameSite 各自防什么","HttpOnly 限制脚本读取，SameSite 明确跨站发送策略，生产还需 Secure。"],
      ["csrf-header","concept-cookie-session","CSRF 为什么使用自定义请求头","CSRF 令牌能放 URL 吗","状态修改携带服务器签发的 X-CSRF-Token，值不进入 URL 或 localStorage。"],
      ["status-401","example-auth-status","什么时候返回 401","WWW-Authenticate 何时出现","缺少、无效、过期或撤销身份返回 401，并附认证挑战。"],
      ["status-403-csrf","example-auth-status","CSRF 错误为什么返回 403","已登录但请求被拒绝是什么状态","身份有效但状态修改缺少正确 CSRF 时返回 403。"],
      ["run-v10","reproduce-dashboard-v10","怎样运行 v0.10 会话测试","Cookie 和 CSRF 测试命令是什么","运行 9 项测试覆盖错误密码、Cookie、身份恢复、CSRF、到期和撤销。"],
      ["modify-expiry","modify-session-expiry","怎样测试会话到期而不等待","缩短会话时间练习怎么做","通过受控时钟或测试辅助函数把到期时间移到过去，再断言认证失败。"],
      ["csrf-troubleshoot","troubleshoot-csrf","POST 返回 403 怎样排查","X-CSRF-Token 不匹配怎么办","依次检查会话 Cookie、当前会话的 CSRF 值和请求头，不关闭防护。"],
      ["project-v10","project-dashboard-v10","v0.10 新增哪些认证接口","为什么不包含注册和 OAuth","项目只增加 login、logout、me 和合成账号，生产身份协议留给后续。"]
    ]
  },
  {
    id:"web-engineering-03", title:"资源所有权、角色授权与审计日志", file:"03-resource-ownership-authorization-audit.md",
    cards:[
      ["authorization-result","overview-resource-authorization","v0.11 最后交付什么","所有权授权课做出什么","v0.11 增加资源所有者、角色动作矩阵、默认拒绝和脱敏审计。"],
      ["owner-field","overview-resource-authorization","owner_user_id 解决什么问题","学习记录怎样归属主体","资源行保存所有者，查询和写入同时按当前主体约束。"],
      ["default-deny","concept-default-deny","为什么未声明动作默认拒绝","权限矩阵没有动作怎么办","没有明确允许的角色动作一律拒绝，避免新接口意外继承权限。"],
      ["learner-role","concept-default-deny","learner 可以执行哪些动作","普通学习者权限边界是什么","学习者只读写自己的学习资源，不能运行操作员诊断。"],
      ["operator-role","concept-default-deny","operator 是不是管理员","操作员能读取所有学习记录吗","操作员只执行明确诊断动作，不因角色名称获得全资源权限。"],
      ["anonymous-401","example-401-403-404","匿名请求为什么是 401","没有 Cookie 访问资源返回什么","请求尚未建立有效身份，因此返回 401 和认证挑战。"],
      ["forbidden-403","example-401-403-404","有效身份越权为什么是 403","角色没有动作权限返回什么","主体已识别但动作未授权，返回 403。"],
      ["hidden-404","example-401-403-404","他人资源为什么返回 404","怎样减少资源枚举","对当前主体不可见的资源统一表现为不存在，避免泄露其存在性。"],
      ["run-v11","reproduce-dashboard-v11","怎样运行 v0.11 授权测试","八项授权审计测试命令是什么","运行 8 项测试覆盖匿名、本人、他人、默认拒绝、角色边界和审计。"],
      ["modify-matrix","modify-permission-matrix","新增权限动作的正确顺序是什么","怎样扩展权限矩阵","先写拒绝测试和动作定义，再只向需要的角色放行。"],
      ["audit-redaction","troubleshoot-audit-redaction","审计日志应该记录什么","哪些认证值不能进入日志","记录主体、动作、资源、结果和 request ID，不记录密码、Cookie、会话或 CSRF 原文。"],
      ["project-v11","project-dashboard-v11","v0.11 的权限证据有哪些","怎样证明资源隔离有效","用权限矩阵和 401/403/404 测试证明身份、动作与所有权三层边界。"]
    ]
  },
  {
    id:"web-engineering-04", title:"会话前端、端到端测试与持续集成", file:"04-session-frontend-e2e-ci.md",
    cards:[
      ["frontend-result","overview-session-frontend","v0.12 最后交付什么","会话前端课做出什么","v0.12 用原生 TypeScript 完成登录、身份恢复、权限状态、退出和 E2E 边界。"],
      ["refresh-me","overview-session-frontend","刷新后怎样恢复身份","为什么刷新要请求 api me","浏览器不保存会话原文，刷新后由 HttpOnly Cookie 配合 /api/me 恢复服务端身份。"],
      ["csrf-memory","concept-memory-csrf","前端把 CSRF 保存在哪里","CSRF 能放 localStorage 吗","CSRF 只存在当前页面内存，退出或刷新后由服务端重新取得。"],
      ["cookie-unreadable","concept-memory-csrf","前端为什么读不到会话 Cookie","HttpOnly 对 TypeScript 有什么影响","HttpOnly 让浏览器随请求发送 Cookie，但不向脚本暴露值。"],
      ["route-401","example-route-status","前端收到 401 做什么","身份失效怎样回登录页","清除身份相关内存状态并路由到登录页。"],
      ["route-403","example-route-status","前端收到 403 做什么","权限不足为什么不当成未登录","保留有效身份，展示动作不被允许的解释和返回路径。"],
      ["logout-state","example-route-status","退出后要清除哪些状态","为什么退出要重置页面状态","服务端撤销会话后，前端清除主体、CSRF、受保护数据和路由状态。"],
      ["run-v12","reproduce-dashboard-v12","怎样运行 v0.12 TypeScript 测试","会话状态机测试命令是什么","安装锁定依赖后运行 npm test，编译并验证 401、403、刷新和退出状态。"],
      ["playwright-real","reproduce-dashboard-v12","为什么 Playwright 要连接真实 PostgreSQL","E2E 可以 mock 数据库吗","关键登录、写入和隔离流程必须跨浏览器、API 与真实数据库验证。"],
      ["modify-a11y","modify-accessible-login","怎样给登录错误增加键盘可达提示","失败提示如何获得焦点","错误区域可聚焦并用语义状态提示，同时不丢失输入和恢复路径。"],
      ["refresh-troubleshoot","troubleshoot-frontend-session","刷新后变匿名怎样排查","api me 返回 401 查什么","检查 Cookie 属性、请求是否携带凭据、会话到期撤销和 /api/me 响应。"],
      ["project-v12","project-dashboard-v12","v0.12 为什么继续使用原生 TypeScript","这课为什么不引入 React","本课目标是会话边界和测试链路，避免框架迁移掩盖状态问题。"]
    ]
  },
  {
    id:"web-engineering-05", title:"容器、配置、健康检查与优雅停止", file:"05-containers-config-health-graceful-shutdown.md",
    cards:[
      ["container-result","overview-container-topology","v0.13 最后交付什么","容器健康课做出什么","v0.13 提供非 root 镜像、app 加数据库拓扑、配置门禁、健康检查和优雅停止。"],
      ["loopback-bind","overview-container-topology","为什么宿主端口只绑定 127.0.0.1","Compose 端口怎样避免外网暴露","教学服务只监听宿主回环地址，降低无意暴露。"],
      ["non-root","overview-container-topology","应用容器为什么使用非 root 用户","Dockerfile USER 有什么用","固定低权限 UID 运行应用，减少容器进程被利用后的权限。"],
      ["liveness","concept-live-ready","liveness 回答什么问题","存活检查能访问数据库吗","存活只确认进程和事件循环仍工作，不依赖数据库。"],
      ["readiness","concept-live-ready","readiness 回答什么问题","数据库未就绪为什么返回 503","就绪表示配置与依赖足以接流量，数据库不可用时必须失败。"],
      ["service-healthy","concept-live-ready","depends_on service_healthy 有什么作用","容器已启动为什么 app 还要等","Compose 等数据库健康检查通过后再启动依赖服务。"],
      ["secret-file","example-secret-file","文件型 secret 与普通环境变量怎样分工","数据库密码放在哪里","普通配置可用环境变量，敏感值通过只读文件注入且不提交真实内容。"],
      ["config-fail-fast","example-secret-file","生产缺少配置为什么拒绝启动","能不能用默认密码继续运行","关键配置缺失立即失败，避免以不安全默认值进入服务状态。"],
      ["run-v13","reproduce-dashboard-v13","怎样验证 v0.13 Compose 拓扑","容器配置测试命令是什么","先运行单测和 docker compose config，再构建并检查非 root、回环端口与健康顺序。"],
      ["modify-readiness","modify-readiness","怎样模拟数据库未就绪","live 正常 ready 503 怎样验证","移除数据库配置或暂停依赖，断言 live 保持正常而 ready 拒绝流量。"],
      ["graceful-stop","troubleshoot-graceful-stop","优雅停止要按什么顺序","停止时怎样保护在途请求","先停止接新流量，等待在途请求，再关闭连接池和进程。"],
      ["project-v13","project-dashboard-v13","v0.13 的部署证据有哪些","怎样证明容器配置安全","保存镜像用户、Compose 渲染、健康响应、缺配置失败和停止测试。"]
    ]
  },
  {
    id:"web-engineering-06", title:"指标、备份、发布与回滚演练", file:"06-observability-backup-release-rollback.md",
    cards:[
      ["release-result","overview-release-evidence","v0.14 最后交付什么","发布回滚课做出什么","v0.14 汇总 JSON 日志、request ID、指标、备份恢复和兼容回滚证据。"],
      ["request-id","overview-release-evidence","request ID 用来做什么","怎样串联一次请求的日志","入口生成或校验 request ID，贯穿响应与结构化日志以关联故障。"],
      ["json-log","overview-release-evidence","结构化 JSON 日志有什么价值","日志为什么不用拼接文本","稳定字段便于过滤、聚合和脱敏检查，并避免依赖脆弱文本解析。"],
      ["expand-contract","concept-expand-contract","expand contract 为什么支持回滚","数据库变更怎样兼容旧镜像","先加兼容结构，再切换读写，确认旧版本不用后才删除旧结构。"],
      ["unsafe-rollback","concept-expand-contract","什么时候必须阻止应用回滚","镜像能启动就能回滚吗","数据库已不兼容旧版本或恢复未验证时，发布门禁必须拒绝回滚。"],
      ["low-cardinality","example-low-cardinality","为什么 request ID 不能做指标标签","高基数指标有什么问题","每请求唯一值会制造海量时间序列；它属于日志，不属于指标标签。"],
      ["metrics-internal","example-low-cardinality","metrics 为什么只对内部开放","Prometheus 指标能公开到公网吗","指标可能暴露路径和运行状态，应在本机或受控内部网络抓取。"],
      ["run-v14","reproduce-dashboard-v14","怎样运行 v0.14 发布门禁测试","八项可观测测试命令是什么","运行 8 项测试验证日志、指标、request ID、恢复证据和回滚门禁。"],
      ["pg-dump-custom","reproduce-dashboard-v14","为什么备份使用 pg_dump custom 格式","自定义备份格式有什么用","custom 格式由 pg_restore 选择性恢复，适合在独立验证库核对。"],
      ["restore-isolated","reproduce-dashboard-v14","为什么恢复到独立验证数据库","能不能直接覆盖正式库验证备份","独立库防止破坏源数据，并允许核对记录、汇总、外键和唯一约束。"],
      ["failure-injection","modify-release-failure","发布故障注入要记录什么","readiness 失败后怎样回滚","记录候选版本、健康失败、停止推进、旧镜像恢复和复核结果。"],
      ["project-v14","project-dashboard-v14","Web 工程化最终交付证据有哪些","v0.14 如何证明可恢复","证据包含测试、健康与指标样本、备份恢复结果、发布记录和故障复盘。"]
    ]
  }
];

for (const lesson of lessons) {
  const page = `learning-paths/web-fullstack/web-engineering/${lesson.file}`;
  const markdown = readFileSync(join(root, page), "utf8");
  const contextMatches = [...markdown.matchAll(/<section data-context-type="([^"]+)" data-learning-context="([^"]+)" id="\2">/g)];
  if (contextMatches.length < 7) throw new Error(`${lesson.id} contexts incomplete`);
  const contexts = contextMatches.map((match) => ({id:match[2], type:match[1], title:match[2].replaceAll("-", " "), anchor:`#${match[2]}`}));
  const contextIds = new Set(contexts.map((item) => item.id));
  const cards = lesson.cards.map(([id, context_id, question, alias, answer]) => {
    if (!contextIds.has(context_id)) throw new Error(`${lesson.id}: missing ${context_id}`);
    return {id, lesson_id:lesson.id, context_id, question:`${question}？`, aliases:[alias], keywords:[...new Set(`${question} ${alias}`.split(/\s+/))], diagnostic:`先确认你正在处理“${alias}”对应的边界，而不是相邻层。`, hints:[`先定位 ${context_id} 中的责任。`,`再用本课固定测试验证 ${question}。`], example:answer, answer, source:{label:contexts.find((item)=>item.id===context_id).title, href:`#${context_id}`}, updated_at:"2026-07-22", recommended:true};
  });
  const knowledge = {version:2, lesson:{id:lesson.id,title:lesson.title,path:`learning-paths/web-fullstack/web-engineering/${lesson.file.replace(/\.md$/, "/")}`}, contexts, cards};
  const fixture = {lesson_id:lesson.id,cases:cards.flatMap((card)=>[{query:card.question.replace(/？$/, ""),expected_card:card.id},{query:card.aliases[0],expected_card:card.id}]),unknown:["怎样在月球海里培育会唱歌的珊瑚","云朵编译成彩虹需要什么参数"]};
  for (const [relative,data] of [[`site-src/data/tutor/${lesson.id}.json`,knowledge],[`tests/tutor/${lesson.id}-search.json`,fixture]]) {
    const target=join(root,relative); mkdirSync(dirname(target),{recursive:true}); writeFileSync(target,JSON.stringify(data,null,2)+"\n");
  }
}

console.log(JSON.stringify({lessons:lessons.length,cards:lessons.reduce((n,item)=>n+item.cards.length,0),questions:lessons.reduce((n,item)=>n+item.cards.length*2,0),unknown:lessons.length*2}));
