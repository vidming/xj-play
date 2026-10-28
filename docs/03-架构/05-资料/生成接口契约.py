"""架构契约生成器；只生成静态规格，不启动HTTP服务或调用支付。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
S = {}


def text(maximum=128, minimum=1, **kw):
    return {"type": "string", "minLength": minimum, "maxLength": maximum, **kw}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def integer(low=0, high=9007199254740991):
    return {"type": "integer", "minimum": low, "maximum": high}


def array(item, maximum=1000, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum, "maxItems": maximum}


def obj(properties, required=None):
    return {"type": "object", "additionalProperties": False,
            "properties": properties, "required": list(properties) if required is None else required}


def ref(name):
    return {"$ref": "#/components/schemas/" + name}


def schema(name, properties, required=None):
    S[name] = obj(properties, required)
    return ref(name)


ID = text(36, 36, format="uuid")
TIME = text(40, format="date-time")
REV = text(20, pattern="^(0|[1-9][0-9]{0,19})$")
KEY = text(128, pattern="^[A-Za-z0-9._:-]+$")
FORMAT = text(128, pattern="^[!-~]+$")
BOOL = {"type": "boolean"}
MONEY = integer(0, 999999)
EMPTY = schema("Empty", {})
ACK = schema("Acknowledgement", {"operationId": ID, "state": enum("ACCEPTED", "PENDING", "SUCCEEDED", "FAILED")})
schema("Error", {
    "code": enum("AUTH_REQUIRED", "EMAIL_VERIFICATION_REQUIRED", "ACCESS_DENIED",
                 "OBJECT_NOT_AVAILABLE", "VALIDATION_FAILED", "QUOTE_CHANGED", "QUOTE_EXPIRED",
                 "SOURCE_PENDING", "SAVE_CONFLICT", "IDEMPOTENCY_MISMATCH", "SAVE_TOO_LARGE",
                 "PROTOCOL_UNSUPPORTED", "SAVE_INCOMPATIBLE", "ACCOUNT_ACTION_RESTRICTED",
                 "RATE_LIMITED", "GAME_SUSPENDED", "DEPENDENCY_UNAVAILABLE", "REVISION_CHANGED",
                 "INTENT_BINDING_INVALID"),
    "msg": text(1000), "requestId": KEY,
    "data": obj({"operationId": ID, "retryAfterSeconds": integer(), "currentRevision": REV,
                 "field": text(128)}, []),
}, ["code", "msg", "requestId"])
schema("BusinessRef", {"type": enum("order", "grant", "upgrade"), "id": ID})
schema("Account", {"subjectId": ID, "nickname": text(24), "emailVerified": BOOL,
                   "lifecycle": enum("ACTIVE", "DELETION_REQUESTED", "PROCESSING", "DELETED", "EXCEPTION")})
schema("Registration", {"email": text(254, format="email"), "password": text(128, 15), "nickname": text(24)})
schema("Login", {"email": text(254, format="email"), "password": text(128, 15),
                 "intentId": {**ID, "description": "可选，仅指定该guest会话原run的单个OPEN意图；公开UUID不是授权证明"}},
       ["email", "password"])
schema("EmailAction", {"email": text(254, format="email")})
schema("TokenAction", {"token": text(512)})
schema("ResetPassword", {"token": text(512), "password": text(128, 15)})
schema("AccountEdit", {"nickname": text(24), "expectedRevision": REV})
schema("EmailChange", {"email": text(254, format="email"), "password": text(128, 15)})
schema("DeletionRequest", {"policyVersion": KEY})
schema("DeletionConfirm", {"expectedRevision": REV, "confirmed": {"const": True}, "token": text(512)})
schema("Deletion", {"id": ID, "state": enum("REQUESTED", "REVIEWING", "AWAIT_CONFIRM", "WITHDRAWN", "PROCESSING", "COMPLETE", "EXCEPTION"),
                    "revision": REV, "blockedBusinessRefs": array(ref("BusinessRef")),
                    "categories": array(obj({"category": KEY, "state": KEY, "nextReviewAt": TIME, "reason": text(1000)}, ["category", "state"]))})
schema("Declarations", {"languages": array(text(32), 20, 1), "devices": array(enum("DESKTOP", "MOBILE"), 2, 1),
                       "contentWarnings": array(text(128), 20), "audio": BOOL, "cloudSave": BOOL})
schema("Product", {"id": ID, "gameId": ID, "kind": enum("BUYOUT", "CHAPTER", "SCENE", "FREE"),
                   "revision": REV, "priceFen": MONEY, "currency": {"const": "CNY"},
                   "promise": text(4000), "contentKeys": array(KEY, 1000, 1),
                   "saleState": enum("DRAFT", "ON_SALE", "DELISTED")})
schema("Game", {"id": ID, "slug": KEY, "title": text(80), "summary": text(160),
                "description": text(2000), "coverResourceId": ID, "screenshotResourceIds": array(ID, 8),
                "declarations": ref("Declarations"), "products": array(ref("Product"), 1000),
                "trialAvailable": BOOL, "publishedAt": TIME, "revision": REV,
                "saleState": enum("DRAFT", "ON_SALE", "DELISTED"),
                "runtimeState": enum("AVAILABLE", "SUSPENDED", "TERMINATING", "CLOSED")})
schema("GameEdit", {"title": text(80), "summary": text(160), "description": text(2000),
                    "coverResourceId": ID, "screenshotResourceIds": array(ID, 8),
                    "declarations": ref("Declarations"), "expectedRevision": REV},
       ["title", "summary", "description", "coverResourceId", "screenshotResourceIds", "declarations"])
schema("RevisionAction", {"expectedRevision": REV, "reason": text(1000)})
schema("Version", {"id": ID, "gameId": ID, "version": KEY, "manifestSha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                   "packageSha256": text(64, 64, pattern="^[a-f0-9]{64}$"), "revision": REV,
                   "state": enum("UPLOADED", "CHECKING", "REVIEW", "PUBLISHED", "REJECTED", "DISABLED"),
                   "updateNotes": text(1000)})
schema("Publish", {"expectedRevision": REV, "validationReceiptId": ID})
schema("Upload", {"fileName": text(255), "byteSize": integer(1), "sha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                  "purpose": enum("COVER", "SCREENSHOT", "GAME_PACKAGE")})
schema("UploadPermit", {"uploadId": ID, "uploadUrl": text(2048, format="uri"),
                        "expiresAt": TIME, "maxBytes": integer(1)})
schema("UploadComplete", {"uploadId": ID, "expectedSha256": text(64, 64, pattern="^[a-f0-9]{64}$")})
schema("VersionCreate", {"uploadId": ID, "manifestSha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                         "updateNotes": text(1000)})
schema("ContentKey", {"id": ID, "gameId": ID, "contentKey": KEY, "meaning": text(1000)})
schema("ContentKeyCreate", {"contentKey": KEY, "meaning": text(1000)})
schema("ProductEdit", {"kind": enum("BUYOUT", "CHAPTER", "SCENE", "FREE"), "priceFen": MONEY,
                       "promise": text(4000), "contentKeys": array(KEY, 1000, 1), "expectedRevision": REV},
       ["kind", "priceFen", "promise", "contentKeys"])
schema("RunCreate", {"gameId": ID, "entryMode": enum("TRIAL", "OWNED", "FREE"), "intentId": ID},
       ["gameId", "entryMode"])
schema("RunResume", {
    "state": enum("AVAILABLE", "UNAVAILABLE"), "handle": text(2048), "versionId": ID,
    "expiresAt": TIME,
    "reason": enum("NO_SAVED_POSITION", "INCOMPATIBLE_VERSION", "EXPIRED", "INTENT_UNAVAILABLE"),
}, ["state"])
S["RunResume"]["allOf"] = [
    {"if": {"properties": {"state": {"const": "AVAILABLE"}}, "required": ["state"]},
     "then": {"required": ["handle", "versionId", "expiresAt"],
              "not": {"required": ["reason"]}}},
    {"if": {"properties": {"state": {"const": "UNAVAILABLE"}}, "required": ["state"]},
     "then": {"required": ["reason"],
              "not": {"anyOf": [{"required": ["handle"]}, {"required": ["versionId"]},
                                {"required": ["expiresAt"]}]}}},
]
schema("RunResource", {
    "path": text(512, pattern="^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[^?#\\x00]+$"),
    "resourceId": ID,
})
schema("Run", {"id": ID, "gameId": ID, "versionId": ID, "mode": enum("TRIAL", "OWNED", "FREE", "PREVIEW"),
               "gameOrigin": text(2048, format="uri"), "entryUrl": text(2048, format="uri"),
               "protocolVersion": {"const": "1.0"}, "capabilities": array(KEY, 20),
               "accessRevision": REV, "expiresAt": TIME, "resourceIndex": array(ref("RunResource"), 10000),
               "resume": ref("RunResume"),
               "subjectPseudonym": text(128), "state": enum("AUTHORIZED", "READY", "EXITED", "FAILED", "REVOKED")},
       ["id", "gameId", "versionId", "mode", "gameOrigin", "entryUrl", "protocolVersion", "capabilities", "accessRevision", "expiresAt", "resourceIndex", "state"])
schema("AccessRequest", {"contentKeys": array(KEY, 1000, 1)})
schema("AccessResult", {"accessRevision": REV, "results": array(obj({
    "contentKey": KEY, "allowed": BOOL, "reason": enum("TRIAL", "GRANTED", "NOT_GRANTED", "SUSPENDED", "UNKNOWN_KEY")}), 1000)})
schema("ResourceRead", {"resourceId": ID})
schema("Ready", {"protocolVersion": {"const": "1.0"}})
schema("Exit", {"reason": enum("USER", "ERROR", "AUTH_EXPIRED", "NAVIGATED")})
schema("PurchaseIntentCreate", {"runId": ID, "contentKeys": array(KEY, 1000, 1), "resumeHandle": text(2048, 0)},
       ["runId", "contentKeys"])
schema("PurchaseIntent", {"id": ID, "gameId": ID, "state": enum("OPEN", "BOUND", "RETURNED", "CANCELLED"),
                          "access": enum("DENIED", "PENDING", "ALLOWED"), "returnAvailable": BOOL,
                          "contentKeys": array(KEY, 1000)})
schema("QuoteCreate", {"productRevisionId": ID, "intentId": ID}, ["productRevisionId"])
schema("CreditSource", {"cashFactId": ID, "netFen": integer(), "allocatedFen": integer(), "revision": REV})
schema("Quote", {"id": ID, "gameId": ID, "productRevisionId": ID, "priceFen": MONEY,
                 "creditFen": MONEY, "dueFen": MONEY, "currency": {"const": "CNY"},
                 "sources": array(ref("CreditSource")), "expiresAt": TIME, "accessRevision": REV})
S["Quote"]["x-cross-field-validation"] = [
    "0<=creditFen<=priceFen且dueFen=priceFen-creditFen；金额只取服务端报价并在确认时重核",
]
S["Quote"]["x-static-cases"] = [
    {"case": "零补款金额关系成立", "schemaValid": True,
     "given": "服务端报价priceFen=1000、creditFen=1000、dueFen=0", "expect": "金额关系成立，允许零补款升级路径继续确认",
     "value": {"id": "123e4567-e89b-42d3-a456-426614174000", "gameId": "123e4567-e89b-42d3-a456-426614174001",
               "productRevisionId": "123e4567-e89b-42d3-a456-426614174002", "priceFen": 1000, "creditFen": 1000,
               "dueFen": 0, "currency": "CNY", "sources": [], "expiresAt": "2026-10-28T12:00:00Z", "accessRevision": "7"}},
    {"case": "正补款金额关系成立", "schemaValid": True,
     "given": "服务端报价priceFen=1000、creditFen=300、dueFen=700", "expect": "金额关系成立，允许正补款订单路径继续确认",
     "value": {"id": "123e4567-e89b-42d3-a456-426614174000", "gameId": "123e4567-e89b-42d3-a456-426614174001",
               "productRevisionId": "123e4567-e89b-42d3-a456-426614174002", "priceFen": 1000, "creditFen": 300,
               "dueFen": 700, "currency": "CNY", "sources": [], "expiresAt": "2026-10-28T12:00:00Z", "accessRevision": "7"}},
    {"case": "拒绝抵扣大于售价", "schemaValid": True, "amountRelationValid": False,
     "given": "priceFen=1000、creditFen=1001、dueFen=0", "expect": "拒绝报价，不进入订单或升级确认",
     "value": {"id": "123e4567-e89b-42d3-a456-426614174000", "gameId": "123e4567-e89b-42d3-a456-426614174001",
               "productRevisionId": "123e4567-e89b-42d3-a456-426614174002", "priceFen": 1000, "creditFen": 1001,
               "dueFen": 0, "currency": "CNY", "sources": [], "expiresAt": "2026-10-28T12:00:00Z", "accessRevision": "7"}},
    {"case": "拒绝应付不等于售价减抵扣", "schemaValid": True, "amountRelationValid": False,
     "given": "priceFen=1000、creditFen=300、dueFen=699", "expect": "拒绝报价，不进入订单或升级确认",
     "value": {"id": "123e4567-e89b-42d3-a456-426614174000", "gameId": "123e4567-e89b-42d3-a456-426614174001",
               "productRevisionId": "123e4567-e89b-42d3-a456-426614174002", "priceFen": 1000, "creditFen": 300,
               "dueFen": 699, "currency": "CNY", "sources": [], "expiresAt": "2026-10-28T12:00:00Z", "accessRevision": "7"}},
]
schema("QuoteConfirm", {"quoteId": ID, "expectedAccessRevision": REV})
schema("Order", {"id": ID, "gameId": ID, "dueFen": MONEY, "currency": {"const": "CNY"},
                 "paymentState": enum("PENDING", "VERIFYING", "PAID", "UNPAID_CLOSED", "EXCEPTION"),
                 "deliveryState": enum("NOT_DUE", "PENDING", "DELIVERED", "EXCEPTION"),
                 "scopeKeys": array(KEY, 1000, 1), "createdAt": TIME, "revision": REV,
                 "supportState": enum("NONE", "OPEN", "CLOSED")})
schema("Upgrade", {
    "id": ID, "gameId": ID, "productRevisionId": ID, "priceFen": MONEY,
    "creditFen": MONEY, "dueFen": MONEY, "currency": {"const": "CNY"},
    "promise": text(4000), "contentKeys": array(KEY, 1000, 1),
    "orderId": ID, "grantId": ID,
    "state": enum("RESERVED", "PENDING", "DELIVERED", "REVIEW", "REVOKED"),
}, ["id", "gameId", "productRevisionId", "priceFen", "creditFen", "dueFen",
    "currency", "promise", "contentKeys", "state"])
S["Upgrade"]["allOf"] = [
    {"if": {"properties": {"state": {"const": "DELIVERED"}}, "required": ["state"]},
     "then": {"required": ["grantId"]}},
    {"if": {"properties": {"dueFen": {"const": 0}}, "required": ["dueFen"]},
     "then": {"not": {"required": ["orderId"]}}},
]
S["Upgrade"]["x-cross-field-validation"] = [
    "productRevisionId、priceFen、promise及contentKeys必须来自同一不可变商品承诺",
    "0<=creditFen<=priceFen且dueFen=priceFen-creditFen；服务端重核，不能采用客户端金额",
    "dueFen=0时orderId为空；dueFen>0时仅在正补款订单由渠道核实并交付后关联",
    "state=DELIVERED时grantId必填；报价内容、金额或访问revision变化均须重新确认",
]
schema("PaymentCreate", {"channel": enum("ALIPAY", "WECHAT"),
                         "method": enum("PAGE", "WAP", "NATIVE", "H5")})
schema("PaymentAction", {"type": enum("FORM", "REDIRECT", "QR"),
                         "expiresAt": TIME, "url": text(2048, format="uri"),
                         "qrText": text(2048), "formHtml": text(12000)},
       ["type", "expiresAt"])
schema("PaymentAttempt", {"id": ID, "orderId": ID, "channel": enum("ALIPAY", "WECHAT"),
                          "method": enum("PAGE", "WAP", "NATIVE", "H5"),
                          "state": enum("CREATING", "WAITING", "UNKNOWN", "SUCCESS", "CLOSED", "FAILED"),
                          "closeState": enum("NONE", "REQUESTED", "CONFIRMED", "UNKNOWN"),
                          "action": ref("PaymentAction")}, ["id", "orderId", "channel", "method", "state", "closeState"])
schema("FreeClaim", {"gameId": ID, "ruleRevision": REV})
schema("Grant", {"id": ID, "gameId": ID, "sourceKind": enum("ORDER", "FREE", "UPGRADE", "COMPENSATION"),
                 "sourceRef": KEY, "state": enum("PENDING", "ACTIVE", "REVIEW", "REVOKED"),
                 "contentKeys": array(KEY), "revision": REV})
schema("ContinueSummary", {
    "available": BOOL, "saveState": enum("NONE", "AVAILABLE", "CONFLICT", "INCOMPATIBLE"),
    "versionId": ID, "lastActivityAt": TIME,
    "accessState": enum("ALLOWED", "DENIED", "PENDING"),
}, ["available", "saveState", "accessState"])
S["ContinueSummary"]["allOf"] = [
    {"if": {"properties": {"available": {"const": True}}, "required": ["available"]},
     "then": {"properties": {"saveState": {"const": "AVAILABLE"}, "accessState": {"const": "ALLOWED"}},
              "required": ["versionId", "lastActivityAt"]}},
]
schema("LibraryItem", {"game": ref("Game"), "grants": array(ref("Grant")),
                       "hasTrialHistory": BOOL, "continue": ref("ContinueSummary")},
       ["game", "grants", "hasTrialHistory"])
schema("SaveMetadata", {"blobId": ID, "format": FORMAT, "byteSize": integer(0, 1048576),
                        "sha256": text(64, 64, pattern="^[a-f0-9]{64}$"), "versionId": ID, "createdAt": TIME})
schema("SaveDescription", {"revision": REV, "current": ref("SaveMetadata"), "previous": ref("SaveMetadata"),
                           "conflict": obj({"id": ID, "left": ref("SaveMetadata"), "right": ref("SaveMetadata")})}, ["revision"])
schema("SaveRead", {"slot": enum("CURRENT", "PREVIOUS", "CONFLICT_LEFT", "CONFLICT_RIGHT"), "expectedRevision": REV})
schema("SavePayload", {"metadata": ref("SaveMetadata"), "revision": REV,
                       "payloadBase64": text(1398104, 0, contentEncoding="base64")})
schema("SaveWrite", {"action": enum("WRITE", "IMPORT", "RESTORE", "RESTART"),
                     "baseRevision": REV, "format": FORMAT, "payloadBase64": text(1398104, 0, contentEncoding="base64"),
                     "sourceBlobId": ID, "conflictId": ID, "confirmed": BOOL},
       ["action", "baseRevision"])
schema("SaveOperation", {"id": ID, "state": enum("ACCEPTED", "PENDING", "SUCCEEDED", "CONFLICT", "FAILED"),
                         "resultRevision": REV, "conflictId": ID}, ["id", "state"])
schema("RestoreConfirm", {"compatible": BOOL, "failureCategory": KEY}, ["compatible"])
schema("SupportCreate", {"businessRef": ref("BusinessRef"),
                         "category": enum("DUPLICATE_PAYMENT", "DELIVERY", "RUNTIME", "VOLUNTARY", "REVOKE", "OTHER"),
                         "description": text(1000)})
schema("Support", {"id": ID, "businessRef": ref("BusinessRef"),
                   "state": enum("ACCEPTED", "REVIEWING", "NEED_INFO", "PROPOSED", "EXECUTING", "CLOSED"),
                   "revision": REV, "nextReviewAt": TIME, "messages": array(obj({
                       "id": ID, "role": enum("PLAYER", "OPERATOR", "SYSTEM"), "text": text(1000), "createdAt": TIME}))})
schema("SupportReply", {"text": text(1000), "expectedRevision": REV})
schema("SupportPlan", {"expectedRevision": REV, "reason": text(1000),
                       "cashRefunds": array(obj({"cashFactId": ID, "amountFen": integer(1)})),
                       "revokeGrantIds": array(ID), "revokeUpgradeIds": array(ID)})
schema("Refund", {"id": ID, "orderId": ID, "cashFactId": ID, "amountFen": integer(1),
                  "cashState": enum("APPROVED", "SENDING", "UNKNOWN", "SUCCEEDED", "FAILED"),
                  "rightsState": enum("PENDING", "ADJUSTED", "EXCEPTION"), "revision": REV})
schema("Report", {"metric": enum(*[f"M-{i:02}" for i in range(1, 12)]), "periodStart": TIME,
                  "periodEnd": TIME, "asOf": TIME, "definitionVersion": KEY,
                  "currency": {"const": "CNY"}, "success": integer(), "failed": integer(),
                  "unknown": integer(), "cancelled": integer(), "sampleCount": integer(),
                  "amountFen": integer(-9007199254740991), "feeState": enum("UNKNOWN", "VERIFIED", "PARTIAL"),
                  "coverage": text(1000)},
       ["metric", "periodStart", "periodEnd", "asOf", "definitionVersion", "currency", "success", "failed", "unknown", "cancelled", "sampleCount", "feeState", "coverage"])
schema("Job", {"id": ID, "state": enum("READY", "LEASED", "DONE", "RETRY", "DEAD"),
               "businessRef": text(128), "nextAttemptAt": TIME, "attempts": integer(), "revision": REV})
schema("Audit", {"id": ID, "operatorRef": KEY, "action": KEY, "businessRef": text(128),
                 "result": KEY, "createdAt": TIME, "traceId": KEY})

# Action-dependent payloads are executable schema constraints, not only prose.
S["SaveWrite"]["allOf"] = [
    {"if": {"properties": {"action": {"enum": ["WRITE", "IMPORT"]}}, "required": ["action"]},
     "then": {"required": ["format", "payloadBase64"]}},
    {"if": {"properties": {"action": {"const": "RESTORE"}}, "required": ["action"]},
     "then": {"required": ["sourceBlobId"]}},
    {"if": {"properties": {"action": {"enum": ["IMPORT", "RESTORE", "RESTART"]}}, "required": ["action"]},
     "then": {"required": ["confirmed"], "properties": {"confirmed": {"const": True}}}},
]
S["PaymentCreate"]["oneOf"] = [
    {"properties": {"channel": {"const": "ALIPAY"}, "method": {"enum": ["PAGE", "WAP"]}}},
    {"properties": {"channel": {"const": "WECHAT"}, "method": {"enum": ["NATIVE", "H5"]}}},
]
S["PaymentAction"]["allOf"] = [
    {"if": {"properties": {"type": {"const": t}}},
     "then": {"required": [field]}}
    for t, field in [("FORM", "formHtml"), ("REDIRECT", "url"), ("QR", "qrText")]
]
for product in ("Product", "ProductEdit"):
    S[product]["allOf"] = [
        {"if": {"properties": {"kind": {"const": "FREE"}}, "required": ["kind"]},
         "then": {"properties": {"priceFen": {"const": 0}}},
         "else": {"properties": {"priceFen": integer(1, 999999)}}}
    ]

# Events share product spelling; source trust is an explicit part of each variant.
event_rows = """
game_detail_expose|WEB|game_ref,view_ref
game_launch_authorize_success|SERVER|run_ref,entry_mode
game_trial_success|GAME|run_ref,entry_mode
order_payment_click|SERVER|order_ref
order_payment_success|SERVER|order_ref,payment_ref
order_payment_fail|SERVER|order_ref,failure_category
entitlement_delivery_success|SERVER|scope_ref
entitlement_delivery_fail|SERVER|order_ref,failure_category
game_launch_success|GAME|run_ref,entry_mode
game_launch_fail|GAME|run_ref,failure_category
game_access_fail|SERVER|failure_category
save_write_success|SERVER|save_revision,operation_ref
save_write_accept_success|SERVER|operation_ref
save_write_fail|SERVER|failure_category,operation_ref
save_restore_success|GAME|save_revision,operation_ref
save_restore_accept_success|SERVER|operation_ref
save_restore_fail|GAME|failure_category,operation_ref
game_release_success|SERVER|version_ref,release_attempt_ref
game_release_accept_success|SERVER|release_attempt_ref,version_ref
game_release_fail|SERVER|version_ref,failure_category,release_attempt_ref
support_request_success|SERVER|businessRef
order_refund_success|SERVER|refund_ref,order_ref
order_refund_fail|SERVER|refund_ref,order_ref,failure_category
account_action_accept_success|SERVER|operation_ref,action_type
account_action_success|SERVER|operation_ref,action_type
account_action_fail|SERVER|operation_ref,action_type,failure_category
order_create_success|SERVER|order_ref,scope_ref
free_claim_accept_success|SERVER|operation_ref,game_ref
free_claim_success|SERVER|operation_ref,scope_ref
free_claim_fail|SERVER|operation_ref,failure_category
game_upgrade_success|SERVER|upgrade_ref,scope_ref
""".strip()
events = []
for line in event_rows.splitlines():
    name, source, fields = line.split("|")
    required = fields.split(",")
    props = {f: (ref("BusinessRef") if f == "businessRef" else KEY) for f in required}
    if name == "game_detail_expose":
        props["source"] = text(128)
    if name == "support_request_success":
        props.update(order_ref=KEY, refund_ref=KEY)
    if name == "entitlement_delivery_success":
        props["order_ref"] = KEY
    if name == "save_restore_fail":
        props["save_revision"] = REV
    if name == "game_access_fail":
        props["scope_ref"] = KEY
    if "entry_mode" in props:
        props["entry_mode"] = enum("TRIAL", "FREE", "OWNED", "PREVIEW")
    if "action_type" in props:
        props["action_type"] = enum("register", "verify", "reset", "delete", "change_email")
    variant = obj({
        "event_ref": {**KEY, "description": "原事件实例编号；同次重试保持编号及载荷；不是数据库全局唯一键或可信付款证明"},
        "type": {"const": name}, "occurred_at": TIME,
        "game_ref": ID, "version_ref": ID, "run_ref": ID,
        "account_ref": KEY, "fields": obj(props, required),
    }, ["event_ref", "type", "occurred_at", "fields"])
    # All runtime identity is canonicalized from run; schema cannot prove origin or truth.
    if source == "GAME":
        variant["required"] += ["game_ref", "version_ref", "run_ref"]
    variant["x-trusted-source"] = source
    variant["x-server-canonicalization"] = "归属/模式/来源由服务端核定；event_key按环境和可信作用域派生，GAME绑定run、WEB绑定平台会话及作品、SERVER绑定持久事件；同键异载荷拒绝，详见数据与运营6.1；游戏结果不证明现金或权益"
    S["Event_" + name] = variant
    events.append((name, source))
S["Event"] = {"oneOf": [ref("Event_" + n) for n, _ in events]}
S["GameEvent"] = {"oneOf": [ref("Event_" + n) for n, source in events if source == "GAME"]}
schema("GameEvents", {"events": array(ref("GameEvent"), 20, 1)})
schema("WebEvents", {"events": array(ref("Event_game_detail_expose"), 20, 1)})
schema("EventReceipt", {"accepted": array(KEY, 20), "duplicates": array(KEY, 20),
                        "rejected": array(obj({"eventRef": KEY, "code": KEY}), 20)})

paths = {}
APP = "/app-api/xj/v1"
ADMIN = "/admin-api/xj/v1"
errors = {"400": "参数/CSRF校验失败", "401": "会话缺失或失效", "403": "验证、权限或归属拒绝",
          "404": "不可见或不存在", "409": "修订、报价或幂等冲突", "413": "请求/存档超限",
          "422": "协议或格式不兼容", "423": "账号生命周期限制", "429": "限流", "503": "依赖或游戏不可用"}


def page(name):
    name_ = name + "Page"
    if name_ not in S:
        schema(name_, {"items": array(ref(name), 100),
                       "pageNo": integer(1), "effectivePageNo": integer(1),
                       "pageSize": integer(1, 100), "total": integer()})
    return name_


def operation(prefix, path, method, name, title, output="Acknowledgement",
              request=None, auth="player", permission=None, paged=False, params=(),
              notes="", status="200", accepted=False):
    params = list(params)
    for token in path.split("/"):
        if token.startswith("{"):
            params.append({"name": token[1:-1], "in": "path", "required": True, "schema": ID})
    if paged:
        output = page(output)
        params += [{"name": "pageNo", "in": "query", "schema": integer(1)},
                   {"name": "pageSize", "in": "query",
                    "schema": {"const": 12} if prefix == APP else integer(1, 100)}]
    if method != "get":
        params.append({"name": "Idempotency-Key", "in": "header", "required": True, "schema": KEY})
        if auth != "admin":
            params.append({"name": "X-CSRF-Token", "in": "header", "required": True, "schema": text(256)})
    response_schema = obj({"code": {"const": 0}, "msg": text(1000, 0),
                           "requestId": KEY, "data": ref(output)})
    responses = {status: {"description": title + "的可信结果",
                          "content": {"application/json": {"schema": response_schema}},
                          "headers": {"Cache-Control": {"schema": {"const": "no-store"}, "description": "私人接口不缓存"}}}}
    for code, desc in errors.items():
        responses[code] = {"description": desc, "content": {"application/json": {"schema": ref("Error")}}}
    if accepted:
        responses["202"] = {"description": "已受理但未完成；按返回业务对象id使用本接口明示的查询路径，结果结构与200一致",
                            "content": {"application/json": {"schema": response_schema}}}
    op = {"operationId": name, "summary": title, "description": notes or title,
          "tags": ["后台" if prefix == ADMIN else "玩家"],
          "parameters": params, "responses": responses,
          "security": ([{"adminBearer": []}] if auth == "admin" else [{"playerSession": []}]),
          "x-authorization": permission or ("公开；不泄露私人对象" if auth == "public" else
                             "验证当前主体与对象归属；新增资产/私人云档另需邮箱已验证"),
          "x-version-policy": "v1重大不兼容变更新major；兼容窗口另定",
          "x-idempotency": "可信主体+动作+对象+key；同key不同payload=409；重试复用key；持久唯一关系兜底",
          "x-runtime-status": "仅设计，尚未实施"}
    if auth == "public":
        op["security"] = []
    if auth == "guest":
        op["x-authorization"] = "平台受控匿名或玩家会话；每次验证run/版本/会话归属；游客仅试玩"
    if request:
        op["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref(request)}}}
    paths.setdefault(prefix + path, {})[method] = op


def query(name, sch):
    return {"name": name, "in": "query", "schema": sch}


operation(APP, "/session", "get", "getSession", "查询当前账号", "Account")
operation(APP, "/guest-sessions", "post", "createGuestSession", "签发匿名试玩会话", auth="public",
          notes="Origin/CSRF引导校验和限流；只签发HttpOnly匿名Cookie，无账号资产", output="RunSession")
schema("RunSession", {"mode": enum("GUEST"), "expiresAt": TIME})
operation(APP, "/csrf", "get", "getCsrfToken", "取得宿主CSRF引导令牌", "Csrf", auth="public")
schema("Csrf", {"token": text(256)})
for path_, name, body, title in [
    ("/accounts", "registerAccount", "Registration", "注册受理"),
    ("/sessions", "loginPlayer", "Login", "玩家登录"),
    ("/email-verifications", "sendVerification", "EmailAction", "发送验证邮件"),
    ("/email-verifications/complete", "completeVerification", "TokenAction", "完成邮箱验证"),
    ("/password-resets", "requestReset", "EmailAction", "找回口令受理"),
    ("/password-resets/complete", "completeReset", "ResetPassword", "重置口令并撤销旧会话"),
]:
    operation(APP, path_, "post", name, title, request=body, auth="public",
              notes="泛化存在性反馈；成功重发才切换旧令牌；60秒/小时5次；token不进URL日志")
operation(APP, "/sessions/current/logout", "post", "logoutPlayer", "退出并撤销当前会话", request="Empty")
operation(APP, "/account/profile", "patch", "editProfile", "更新玩家昵称", "Account", "AccountEdit")
operation(APP, "/account/email-change", "post", "changeEmail", "请求变更邮箱", request="EmailChange")
operation(APP, "/account/deletion", "post", "requestDeletion", "申请分类注销", "Deletion", "DeletionRequest")
operation(APP, "/account/deletion", "get", "getDeletion", "查询注销分类状态", "Deletion")
operation(APP, "/account/deletion/confirm", "post", "confirmDeletion", "最终确认注销并立刻撤会话", "Deletion", "DeletionConfirm")
operation(APP, "/account/deletion/withdraw", "post", "withdrawDeletion", "最终确认前撤回注销", "Deletion", "RevisionAction")
operation(APP, "/games", "get", "listGames", "发现与筛选已公开作品", "Game", auth="public", paged=True,
          params=[query("keyword", text(100, 0)), query("mode", enum("ALL", "FREE", "BUYOUT", "CHAPTER", "SCENE")),
                  query("device", enum("DESKTOP", "MOBILE")), query("sort", enum("PUBLISHED_DESC"))])
operation(APP, "/games/{gameId}", "get", "getGame", "查询公开作品详情", "Game", auth="public")
operation(APP, "/web-events", "post", "reportWebEvents", "记录详情观察事件", "EventReceipt", "WebEvents", auth="public")
operation(APP, "/runs", "post", "createRun", "核实范围后创建运行", "Run", "RunCreate", auth="guest")
operation(APP, "/runs/{runId}/context", "get", "getRunContext", "取得最小运行上下文", "Run", auth="guest")
operation(APP, "/runs/{runId}/access/check", "post", "checkAccess", "核对当前内容权限", "AccessResult", "AccessRequest", auth="guest")
operation(APP, "/runs/{runId}/resources/read", "post", "readResource", "读取已发布且当前获准资源", "Empty", "ResourceRead", auth="guest",
          notes="由宿主代调；当前会话/run/版本/内容全检查；拒绝任意URL；Content-Type按已审核MIME；nosniff/no-store")
paths[APP + "/runs/{runId}/resources/read"]["post"]["responses"]["200"] = {
    "description": "受控二进制；审核MIME、nosniff、no-store；游戏经MessagePort接收ArrayBuffer",
    "content": {"application/octet-stream": {"schema": {"type": "string", "contentEncoding": "binary"}}},
    "headers": {"Content-Type": {"schema": text(128)}, "Cache-Control": {"schema": {"const": "no-store"}},
                "X-Content-Type-Options": {"schema": {"const": "nosniff"}},
                "X-Resource-SHA256": {"schema": text(64, 64)}}}
operation(APP, "/runs/{runId}/ready", "post", "readyRun", "声明已可交互并核验运行", "Run", "Ready", auth="guest")
operation(APP, "/runs/{runId}/exit", "post", "exitRun", "关闭当前运行桥", request="Exit", auth="guest")
operation(APP, "/purchase-intents", "post", "createIntent", "登记原游戏购买返回意图", "PurchaseIntent", "PurchaseIntentCreate", auth="guest")
operation(APP, "/purchase-intents/{intentId}/bind", "post", "bindIntent", "登录后核验并承接匿名意图", "PurchaseIntent", "Empty",
          notes="必须核验原游客会话、指定意图与新登录会话的服务端交接；仅持intentId不足以认领")
operation(APP, "/purchase-intents/{intentId}", "get", "getIntent", "查询购买返回及当前访问状态", "PurchaseIntent", auth="guest")
operation(APP, "/quotes", "post", "createQuote", "生成10分钟服务端报价", "Quote", "QuoteCreate")
operation(APP, "/orders", "post", "createOrder", "重核报价并创建正应付订单", "Order", "QuoteConfirm",
          notes="dueFen必须>0；不接受客户端金额；零补款返回409并引导独立upgrade操作")
operation(APP, "/upgrades", "post", "createUpgrade", "重核并创建零补款升级", "Upgrade", "QuoteConfirm",
          notes="该入口只接dueFen=0；不制造支付订单；正补款订单核实交付后关联升级")
operation(APP, "/orders", "get", "listOrders", "查询本人订单", "Order", paged=True)
operation(APP, "/orders/{orderId}", "get", "getOrder", "分开查询付款交付售后状态", "Order")
operation(APP, "/orders/{orderId}/payment-attempts", "post", "createPayment", "选择支付宝或微信付款尝试", "PaymentAttempt", "PaymentCreate",
          notes="首期仅接受支付宝PAGE/WAP与微信NATIVE/H5；JSAPI及小程序不在首期；服务端验证浏览器/商户产品资格、可支付状态与渠道切换守卫；旧尝试UNKNOWN先核实，不靠新out_trade_no重试")
operation(APP, "/payment-attempts/{attemptId}", "get", "getPayment", "查询本人付款尝试", "PaymentAttempt")
operation(APP, "/payment-attempts/{attemptId}/reconcile", "post", "reconcilePayment", "请求有界可信查单", "PaymentAttempt", "Empty")
operation(APP, "/orders/{orderId}/close", "post", "closeOrder", "请求关单并等待渠道核实", "Order", "RevisionAction")
operation(APP, "/claims/free", "post", "claimFree", "已验证账号免费领取", "Grant", "FreeClaim")
operation(APP, "/library", "get", "getLibrary", "分别返回授予与试玩记录", "LibraryItem", paged=True)
operation(APP, "/upgrades/{upgradeId}", "get", "getUpgrade", "查询本人差价升级", "Upgrade")
operation(APP, "/runs/{runId}/save", "get", "describeSave", "查询当前档恢复点及冲突", "SaveDescription")
operation(APP, "/runs/{runId}/save/read", "post", "readSave", "受控读取选定存档来源", "SavePayload", "SaveRead")
operation(APP, "/runs/{runId}/save-operations", "post", "operateSave", "提交CAS保存导入恢复重开", "SaveOperation", "SaveWrite",
          notes="WRITE/IMPORT需format+payload，RESTORE需sourceBlobId，RESTART/IMPORT/RESTORE需confirmed=true；读取来源走save/read，兼容确认走restore-confirm，不以READ_RESTORE动作冒充恢复；此值仅为宿主确认后的意图，不是授权证明；宿主确认绑定当前主体/run/action/baseRevision及payload摘要或sourceBlobId；服务端仍验证归属/CAS/幂等；编码后未压缩<=1048576字节；第三冲突源拒收并留来源端；202仍返回SaveOperation，按id查询GET /save-operations/{operationId}",
          accepted=True)
operation(APP, "/save-operations/{operationId}", "get", "getSaveOperation", "查同次保存操作结果", "SaveOperation")
operation(APP, "/save-operations/{operationId}/restore-confirm", "post", "confirmRestore", "游戏报告兼容恢复结果", "SaveOperation", "RestoreConfirm",
          notes="宿主核对本run/操作/来源；游戏报告仅解释存档兼容，不赋予权益")
operation(APP, "/runs/{runId}/events", "post", "reportGameEvents", "接收游戏来源白名单事件", "EventReceipt", "GameEvents", auth="guest")
operation(APP, "/support-cases", "post", "createSupport", "登记订单授予或升级售后", "Support", "SupportCreate")
operation(APP, "/support-cases", "get", "listSupport", "查询本人售后", "Support", paged=True)
operation(APP, "/support-cases/{supportId}", "get", "getSupport", "查询本人售后进度", "Support")
operation(APP, "/support-cases/{supportId}/messages", "post", "replySupport", "补充售后说明", "Support", "SupportReply")

# Admin bearer retains system authentication, with new explicit object-scope permissions.
admin_rows = [
    ("/games", "get", "adminListGames", "作品管理列表", "Game", None, "game:read", True),
    ("/games", "post", "adminCreateGame", "新建作品草稿", "Game", "GameEdit", "game:write", False),
    ("/games/{gameId}", "patch", "adminEditGame", "修订作品展示资料", "Game", "GameEdit", "game:write", False),
    ("/games/{gameId}/state", "post", "adminChangeGameState", "停售暂停或终止服务", "Game", "GameStateChange", "game:operate", False),
    ("/uploads", "post", "adminRequestUpload", "申请受限资源上传", "UploadPermit", "Upload", "release:upload", False),
    ("/uploads/complete", "post", "adminCompleteUpload", "核对真实对象摘要及扫描", "Acknowledgement", "UploadComplete", "release:upload", False),
    ("/games/{gameId}/versions", "post", "adminCreateVersion", "登记不可变版本", "Version", "VersionCreate", "release:write", False),
    ("/games/{gameId}/versions", "get", "adminListVersions", "查询作品版本", "Version", None, "release:read", True),
    ("/game-versions/{versionId}/validate", "post", "adminValidateVersion", "接入包验证受理", "Acknowledgement", "RevisionAction", "release:review", False),
    ("/game-versions/{versionId}/preview", "post", "adminPreviewVersion", "签发受限预览运行", "Run", "RevisionAction", "release:preview", False),
    ("/game-versions/{versionId}/publish", "post", "adminPublishVersion", "校验后发布指定版本", "Acknowledgement", "Publish", "release:publish", False),
    ("/games/{gameId}/content-keys", "post", "adminCreateContent", "登记稳定内容含义", "ContentKey", "ContentKeyCreate", "catalog:write", False),
    ("/games/{gameId}/products", "get", "adminListProducts", "查询商品承诺版本", "Product", None, "catalog:read", True),
    ("/games/{gameId}/products", "post", "adminCreateProduct", "新建不可变商品承诺", "Product", "ProductEdit", "catalog:write", False),
    ("/products/{productId}/state", "post", "adminProductState", "变更商品售卖状态", "Product", "ProductStateChange", "catalog:operate", False),
    ("/orders", "get", "adminListOrders", "受限查询订单", "Order", None, "trade:read", True),
    ("/orders/{orderId}", "get", "adminGetOrder", "核对付款交付与售后", "Order", None, "trade:read", False),
    ("/orders/{orderId}/reconcile", "post", "adminReconcileOrder", "受控查证所有支付尝试", "Acknowledgement", "RevisionAction", "trade:reconcile", False),
    ("/support-cases", "get", "adminListSupport", "查询售后与超时队列", "Support", None, "support:read", True),
    ("/support-cases/{supportId}/messages", "post", "adminReplySupport", "人工更新处理记录", "Support", "SupportReply", "support:write", False),
    ("/support-cases/{supportId}/plan", "post", "adminProposePlan", "记录现金与来源处置方案", "Support", "SupportPlan", "support:approve", False),
    ("/support-cases/{supportId}/execute", "post", "adminExecutePlan", "执行已批准售后方案", "Acknowledgement", "RevisionAction", "support:execute", False),
    ("/refunds", "get", "adminListRefunds", "查询现金与撤权分别状态", "Refund", None, "refund:read", True),
    ("/refunds/{refundId}/execute", "post", "adminExecuteRefund", "执行原路退款并保留额度", "Refund", "RevisionAction", "refund:execute", False),
    ("/refunds/{refundId}/reconcile", "post", "adminReconcileRefund", "查证原退款号", "Refund", "RevisionAction", "refund:reconcile", False),
    ("/reports", "get", "adminReports", "区间指标及可信现金核对", "Report", None, "report:read", False),
    ("/jobs", "get", "adminListJobs", "查看补偿清理与发布任务", "Job", None, "operations:read", True),
    ("/jobs/{jobId}/retry", "post", "adminRetryJob", "重试同业务任务", "Job", "RevisionAction", "operations:retry", False),
    ("/audit-events", "get", "adminAudit", "最小必要审计查询", "Audit", None, "audit:read", True),
]
schema("GameStateChange", {"expectedRevision": REV, "saleState": enum("DRAFT", "ON_SALE", "DELISTED"),
                           "runtimeState": enum("AVAILABLE", "SUSPENDED", "TERMINATING", "CLOSED"),
                           "reason": text(1000), "servicePlanRef": ID}, ["expectedRevision", "reason"])
schema("ProductStateChange", {"expectedRevision": REV, "saleState": enum("ON_SALE", "DELISTED"), "reason": text(1000)})
for p, method, name, title, output, request, permission, paged in admin_rows:
    operation(ADMIN, p, method, name, title, output, request, auth="admin", permission="xj:" + permission + " + 服务端作品/对象作用域", paged=paged)
paths[ADMIN + "/reports"]["get"]["parameters"] += [
    query("metric", S["Report"]["properties"]["metric"]), query("start", TIME), query("end", TIME),
    query("asOf", TIME), query("gameId", ID), query("currency", {"const": "CNY"})]
paths[ADMIN + "/reports"]["get"]["description"] = "区间左闭右开，Asia/Shanghai；1–366日；asOf修订；30日外明细不凭空恢复，覆盖不足如实标注"

paths[APP + "/runs"]["post"]["description"] += (
    "；可选intentId只接受公开意图编号，服务端核对当前会话、已绑定意图、作品、当前访问和版本后，"
    "才通过Run.resume交付受控位置；不存在或不属于当前绑定返回INTENT_BINDING_INVALID。"
    "RunResume.versionId必须等于本次Run.versionId，位置不授权、不跨版本静默复用、不写URL或日志。"
)
paths[APP + "/purchase-intents/{intentId}"]["get"]["description"] += (
    "；只返回绑定、状态、当前访问及returnAvailable，不回显resumeHandle或可直接恢复的位置。"
)
paths[APP + "/library"]["get"]["description"] += (
    "；continue仅返回可用性、保存状态、适用版本、最近活动及访问状态，不返回payload、剧情文本、"
    "资源路径或原始handle；摘要不证明读档成功或授予权益。"
)

# GI-A：同浏览器服务端短时一次性交接。公开意图编号不能替代会话证明。
guest_session = paths[APP + "/guest-sessions"]["post"]
guest_session["description"] += "；200 Set-Cookie明确签发__Host-xj-session；令牌不放响应体/URL/日志。"
guest_session["responses"]["200"]["headers"]["Set-Cookie"] = {
    "schema": {"type": "string"},
    "description": "__Host-xj-session=<服务端生成不透明令牌>; Path=/; Secure; HttpOnly; SameSite=Lax；不设置Domain。"
                   "成功仅签发GUEST不透明令牌；同名Cookie覆盖旧值，按服务端会话记录校验，不在JSON返回令牌",
}
login = paths[APP + "/sessions"]["post"]
schema("LoginResult", {
    "state": {"const": "SUCCEEDED"},
    "handoffError": obj({"code": {"const": "INTENT_BINDING_INVALID"}, "msg": text(1000)},
                        ["code", "msg"]),
}, ["state"])
S["LoginResult"]["properties"]["handoffError"]["description"] = (
    "可选；仅表示认证成功后未创建交接，不含对象存在性、取消、过期、Cookie或会话谱系细节"
)
login["responses"]["200"]["content"]["application/json"]["schema"]["properties"]["data"] = ref("LoginResult")
login["description"] = (
    "账号密码登录；注册仅返回Acknowledgement，注册后须显式登录。可选intentId只为请求时当前有效guest Cookie对应的原guest run之单个OPEN意图创建交接；"
    "必须先核账号密码成功、当前guest Cookie解析的session.id须精确等于意图guest_session_id及原run.session_id；guest会话在登录时有效、"
    "意图在原run有效时创建及历史run/session/作品/版本归属与30分钟登录交接资格，再在同库事务中创建目标PLAYER会话、唯一intent交接和幂等结果，"
    "最后在200 Set-Cookie签发PLAYER Cookie并在服务端撤销原guest令牌（仅保留交接历史快照）。账号密码认证失败才使登录失败；"
    "认证成功后无有效guest Cookie、intentId无可信交接资格或意图不再OPEN时登录仍成功、签发PLAYER Cookie但不创建交接，响应不区分这些原因。"
    "交接失败只产生与绑定失败相同的泛化INTENT_BINDING_INVALID摘要，放在200 data.handoffError且不改变登录state=SUCCEEDED；"
    "不透露不存在、取消、过期或Cookie/谱系细节，不能把它当作密码认证失败。"
    "若创建意图后、登录前guest轮换为另一session记录且无服务端可信轮换谱系，不建交接并泛化提示重新选择商品；只持公开intentId不能认领，也不扫描该guest其他意图。"
    "相同登录Idempotency-Key及规范化请求经原guest令牌摘要对应的已成功结果或原结果对应PLAYER Cookie识别重试，只复用同一会话/交接并重发原PLAYER Cookie结果；"
    "已撤销guest令牌不能发起新交接，不延长期限；不同账号、不同请求复用key泛化拒绝。无intentId则普通登录。"
    "原run可在登录页打开后正常EXITED；不要求登录时仍READY/活跃。普通run退出或登录后guest令牌撤销不废止已创建的交接；"
    "安全撤销/游戏暂停可使位置不可用，不抹已核实付款事实。邮箱验证可在绑定后完成，但购买前必须验证；60秒/小时5次；token不进URL日志。"
)
login["x-authorization"] = (
    "公开账号密码登录；intentId交接须同一可信请求携当前有效guest Cookie与CSRF，目标账号仅来自成功认证，不能由intentId授权；"
    "登录前guest当前session.id必须等于意图原会话，异session且无服务端可信轮换谱系拒绝，不凭同浏览器推断"
)
login["x-idempotency"] = (
    "原guest会话+登录动作+key+规范化请求；同key重试复用目标session、handoff和响应，不重新签发会话或延长有效期；"
    "响应重试只查原guest令牌摘要已提交结果或已签发的同一PLAYER会话；撤销guest令牌不能再新建交接；异账号/异载荷泛化拒绝"
)
login["responses"]["200"]["headers"]["Set-Cookie"] = {
    "schema": {"type": "string"},
    "description": "__Host-xj-session=<服务端生成不透明令牌>; Path=/; Secure; HttpOnly; SameSite=Lax；不设置Domain。"
                   "成功签发PLAYER不透明令牌并覆盖同名guest/旧PLAYER Cookie；原guest令牌在服务端撤销，交接只依已持久化的登录时有效快照，"
                   "旧Cookie不能继续访问GUEST API；幂等重试重发原PLAYER Cookie结果，不另建交接",
}
login["x-static-cases"] = [
    {"case": "认证成功且交接资格有效", "schemaValid": True,
     "request": {"email": "player@example.com", "password": "example-passphrase", "intentId": "123e4567-e89b-42d3-a456-426614174000"},
     "given": "同一可信登录请求有当前有效guest Cookie、原run有效时创建的指定OPEN意图；原run现可正常EXITED；成功认证",
     "expect": "登录成功；仅该intent创建一次交接；同键重试原会话与交接结果"},
    {"case": "拒绝请求结构", "schemaValid": False,
     "request": {"email": "player@example.com", "password": "example-passphrase", "intentId": "not-a-uuid"},
     "given": "intentId不是UUID，尚未执行账号密码认证",
     "expect": "认证前400格式校验失败；不创建会话或交接"},
    {"case": "密码账号认证失败才登录失败", "schemaValid": True,
     "request": {"email": "player@example.com", "password": "example-passphrase", "intentId": "123e4567-e89b-42d3-a456-426614174000"},
     "given": "账号密码认证失败，不进入交接判断",
     "expect": "登录失败；不创建PLAYER会话或交接；不因intentId改变认证结果"},
    {"case": "认证成功但guest Cookie或意图不满足交接", "schemaValid": True,
     "request": {"email": "player@example.com", "password": "example-passphrase", "intentId": "123e4567-e89b-42d3-a456-426614174000"},
     "given": "账号密码认证成功；无有效guest Cookie、无交接资格或意图非OPEN中的任一情况",
     "expect": "登录仍成功并签发PLAYER Cookie；不创建交接；仅泛化INTENT_BINDING_INVALID摘要且不泄漏具体原因"},
]

create_run = paths[APP + "/runs"]["post"]
create_run["description"] = (
    "核实范围后创建运行；可选intentId只接受公开意图编号，服务端核当前PLAYER会话/账号与GI-A绑定或PLAYER直达创建的BOUND意图目标一致、"
    "RunCreate.gameId必须等于意图gameId，目标范围按意图contentKeys逐key重核当前权益或试玩规则，不由客户端另传或扩大。"
    "位置仍在绑定后24小时保留窗口、未被安全撤销/游戏暂停且作品/精确版本匹配。原run正常EXITED不影响绑定，但每次独立核当前权益和目标版本后，"
    "才经Run.resume交付受控位置；不凭BOUND、RETURNED或位置授予权限。缺失、作品/范围/主体不符返回泛化INTENT_BINDING_INVALID。"
    "首次交付按固定锁序在同事务内创建run、固定唯一return_run_id并将BOUND原子转为RETURNED；已RETURNED只接受return_run_id精确等于本次已持久run的原键原请求重放，返回同一结果。"
    "同键异规范化请求、换键再交付或换run重放均拒绝，不覆盖return_run_id、不创建第二个承接run。"
    "RunResume.versionId须等于本次Run.versionId，位置不跨版本复用、不写URL或日志。"
)
create_run["x-idempotency"] = (
    "当前可信GUEST/PLAYER会话+createRun+对象作用域+Idempotency-Key+规范化请求；携intentId时对象作用域为该意图，"
    "无intentId时为当前会话+gameId+entryMode+适用版本/模式的创建作用域；同会话同对象同键同请求重放原run，同键异请求拒绝，换键是独立运行申请。"
    "GUEST无intentId仅限TRIAL；携BOUND/RETURNED意图仅当前PLAYER会话可用。"
    "首次成功原子写return_run_id与BOUND→RETURNED；"
    "RETURNED+return_run_id仅重放同键同请求的同一run/RunResume；同键异请求、换键或换run拒绝"
)
create_run["x-static-cases"] = [
    {"case": "BOUND首次交付原子转为RETURNED", "schemaValid": True,
     "request": {"gameId": "123e4567-e89b-42d3-a456-426614174000", "entryMode": "OWNED", "intentId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "意图BOUND于当前主体，gameId相等，目标范围按intent content_keys核验且位置/版本有效",
     "expect": "同事务创建run并固定return_run_id，BOUND原子转RETURNED；同键重试返回原run"},
    {"case": "RETURNED加return_run_id重放原结果", "schemaValid": True,
     "request": {"gameId": "123e4567-e89b-42d3-a456-426614174000", "entryMode": "OWNED", "intentId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "意图已RETURNED，持久return_run_id等于首次成功run；同主体同键同规范化请求",
     "expect": "返回同一run及原RunResume，不创建新run、不重新消费位置"},
    {"case": "游客无意图创建与重放", "schemaValid": True,
     "request": {"gameId": "123e4567-e89b-42d3-a456-426614174000", "entryMode": "TRIAL"},
     "given": "当前有效GUEST会话、无意图、TRIAL请求合法；对象作用域为会话+gameId+entryMode+适用版本/模式",
     "expect": "首次创建游客run；同会话同对象同键同请求重放原run，同键异请求拒绝，不涉及return_run_id"},
    {"case": "拒绝作品或意图范围不符", "schemaValid": True,
     "request": {"gameId": "123e4567-e89b-42d3-a456-426614174009", "entryMode": "OWNED", "intentId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "RunCreate.gameId与意图作品不同，或目标范围未通过intent content_keys的当前权限核验",
     "expect": "泛化INTENT_BINDING_INVALID；不创建run、不交付位置、不改变意图"},
    {"case": "拒绝换键换run或同键异请求", "schemaValid": True,
     "request": {"gameId": "123e4567-e89b-42d3-a456-426614174000", "entryMode": "OWNED", "intentId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "同键不同规范化请求，或已RETURNED后换键/换run请求再次交付",
     "expect": "拒绝并保留原return_run_id；不覆盖原结果、不创建第二个承接run"},
]
intent = paths[APP + "/purchase-intents"]["post"]
intent["description"] = (
    "由当前有效GUEST或PLAYER Cookie及归属一致的可信有效run创建购买返回意图；服务端核run.session_id、subject、版本所属作品、内容范围与当前访问/权益，"
    "不凭客户端提供的账号或intentId授权。GUEST原TRIAL run创建OPEN匿名意图，服务端固化原guest会话与run/版本/作品；创建后run正常EXITED不阻断交接，"
    "创建后30分钟内且guest登录时仍有效才可发起GI-A。PLAYER run直接用服务端当前PLAYER会话及其subject原子创建BOUND意图，bound_at/目标会话当场写入，"
    "无guest_session_id、无需登录或handoff；后续位置仍须再核当前会话/权益及精确版本。resumeHandle不含凭据且不回显；报价10分钟独立，购买前需邮箱已验证。"
)
intent["x-authorization"] = (
    "当前有效GUEST或PLAYER Cookie、CSRF与run.session_id一致；PLAYER subject取服务端会话并与run归属核对，GUEST只准TRIAL；"
    "服务端核作品/版本/内容/权益，不接受客户端指定目标账号"
)
intent["x-static-cases"] = [
    {"case": "GUEST有效", "schemaValid": True, "given": "当前有效GUEST Cookie与TRIAL run匹配，创建时run有效，内容/作品/版本核对",
     "expect": "OPEN、guest_session_id非空、subject_id和bound_player_session_id为空，登录后才可GI-A",
     "request": {"runId": "123e4567-e89b-42d3-a456-426614174001", "contentKeys": ["chapter.1"], "resumeHandle": "scene-1"}},
    {"case": "PLAYER有效", "schemaValid": True, "given": "当前有效PLAYER Cookie与同账号PLAYER run匹配，作品/版本/内容/访问权益核对",
     "expect": "直接BOUND，subject_id、bound_player_session_id和bound_at非空；guest_session_id和handoff为空",
     "request": {"runId": "123e4567-e89b-42d3-a456-426614174001", "contentKeys": ["chapter.1"], "resumeHandle": "scene-1"}},
    {"case": "拒绝", "schemaValid": True, "given": "客户端自报账号、run与当前Cookie不一致、版本/内容/权益不符；或当前guest已轮换但试图使用旧run",
     "expect": "泛化归属或权限错误，不创建意图",
     "request": {"runId": "123e4567-e89b-42d3-a456-426614174001", "contentKeys": ["chapter.1"], "resumeHandle": "scene-1"}},
    {"case": "拒绝schema", "schemaValid": False,
     "request": {"runId": "123e4567-e89b-42d3-a456-426614174001", "contentKeys": ["chapter.1"], "resumeHandle": "scene-1", "subjectId": "123e4567-e89b-42d3-a456-426614174002"},
     "given": "客户端额外提交subjectId，试图自报目标账号",
     "expect": "400额外字段拒绝；不得自报目标账号"},
]
bind = paths[APP + "/purchase-intents/{intentId}/bind"]["post"]
bind["description"] = (
    "仅GUEST创建的OPEN意图执行此空请求bind；PLAYER直达意图在创建时已BOUND，不调用bind。请求体必须为空。"
    "首次bind由当前PLAYER Cookie解析目标会话/账号，以同库intent唯一handoff核验当前PLAYER session.id精确匹配handoff.player_session_id和subject"
    "（无已实现的可信轮换谱系时不同session一律拒绝并重新选择商品）、原guest session/run/版本/作品、OPEN、意图创建时原run有效及历史归属、"
    "登录时guest有效的交接快照、handoff期限与未取消/安全撤销/消费；固定锁序在同事务内绑定账号/目标会话并消费handoff。公开intentId不授权。"
    "换号、guest登录前无谱系轮换或PLAYER登录后bind前无谱系轮换、跨浏览器、未建交接前意图登录资格过期或交接到期、取消、撤销或目标旧会话、重复消费统一泛化INTENT_BINDING_INVALID，"
    "不回显位置或存在性；同目标会话同Idempotency-Key在首次成功后返回原稳定结果。建议登录资格在创建后30分钟内且登录时guest有效；"
    "已成功登录的handoff再保留15分钟，不因原run正常EXITED或guest Cookie轮换/自然到期失效。位置绑定后24小时保留，"
    "安全撤销/游戏暂停可使位置不可用但不抹付款事实；邮箱验证可在bind后但购买前完成。"
)
bind["x-authorization"] = (
    "仅当前有效PLAYER Cookie；GUEST意图须按同库唯一handoff核目标session/subject和原guest session/run/版本/作品历史快照及创建/登录时点；"
    "PLAYER直达BOUND意图不适用；不接受客户端会话或账号证明；PLAYER轮换为另一session记录且无服务端可信轮换谱系则泛化拒绝并重新选择商品，不凭同浏览器放行"
)
bind["x-idempotency"] = "首次bind将目标会话/账号及作用域Idempotency-Key摘要持久化并原子消费handoff；同会话同键稳定返回，换键/换号/换会话拒绝"
bind["x-static-cases"] = [
    {"case": "允许", "schemaValid": True, "given": "登录时同浏览器guest Cookie有效且指定原run有效时创建的OPEN意图；原run现可EXITED；目标PLAYER Cookie与handoff匹配且未过期",
     "expect": "同库首次BOUND并CONSUMED；同会话同键重试返回原结果", "request": {}},
    {"case": "拒绝", "schemaValid": True, "given": "仅有公开intentId，或另一浏览器/账号/目标会话，或未建交接前意图过期/交接到期/取消/撤销/已消费，或原guest会话/run/版本/作品不匹配；或guest在登录前/PLAYER在bind前轮换为另一session且无服务端可信轮换谱系",
     "expect": "泛化INTENT_BINDING_INVALID；无位置/归属泄露，无新交接", "request": {}},
    {"case": "拒绝schema", "schemaValid": False, "request": {"guestSessionId": "伪造"},
     "given": "客户端额外提交guestSessionId，试图自报游客会话证明",
     "expect": "400额外字段拒绝；不使用客户端交接证明"},
]
paths[APP + "/purchase-intents/{intentId}"]["get"]["description"] = (
    "仅当前有权guest原会话或首次绑定/PLAYER直达创建的目标PLAYER会话/账号可查询购买返回状态；公开intentId本身不授权。"
    "只返回绑定、当前访问及returnAvailable，不回显resumeHandle或可直接恢复的位置；未交接意图的登录资格过期、交接到期、取消及换号泛化拒绝；"
    "已绑定意图由当前目标会话按归属查询。 会话轮换不能凭同浏览器推定归属；无可信轮换谱系按新session拒绝。"
)
quote = paths[APP + "/quotes"]["post"]
quote["description"] = (
    "已验证邮箱的当前PLAYER会话生成10分钟服务端报价；若携intentId，须核该意图已BOUND于当前会话/账号、作品与目标商品修订及contentKeys覆盖相符，"
    "位置的24小时期限不替代报价期限或付款资格；不携intentId的普通商品购买仍按账号、商品与权益独立核验。金额由服务端计算，提交订单时重核修订和报价有效期。"
)
quote["x-authorization"] = (
    "仅已验证邮箱的当前PLAYER会话；可选intentId须为当前会话/账号绑定的BOUND意图，且目标商品版本/作品/内容范围匹配；"
    "公开intentId不授权，过期位置不影响已付款事实"
)
quote["x-static-cases"] = [
    {"case": "普通购买报价可不携意图", "schemaValid": True,
     "request": {"productRevisionId": "123e4567-e89b-42d3-a456-426614174000"},
     "given": "当前PLAYER已验证邮箱，商品修订有效且按当前账号/权益生成报价",
     "expect": "创建服务端报价；不伪造购买返回绑定"},
    {"case": "携意图报价须绑定当前主体", "schemaValid": True,
     "request": {"productRevisionId": "123e4567-e89b-42d3-a456-426614174000", "intentId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "意图BOUND于当前会话/账号，作品/目标商品修订及contentKeys覆盖相符",
     "expect": "创建服务端报价；提交确认仍重核全部守卫"},
    {"case": "拒绝携入目标主体字段", "schemaValid": False,
     "request": {"productRevisionId": "123e4567-e89b-42d3-a456-426614174000", "subjectId": "123e4567-e89b-42d3-a456-426614174001"},
     "given": "客户端额外提交subjectId，试图自报报价目标主体",
     "expect": "400额外字段拒绝；主体只取当前PLAYER会话"},
]

quote_confirmation_guard = (
    "服务端锁序内确认报价属于当前PLAYER主体，且QuoteConfirm.expectedAccessRevision == quote.access_revision == 当前权益守卫revision；"
    "重核报价有效期、不可变商品修订、contentKeys、合格抵扣来源的归属/净实付/已分配/在途抵扣与revision，"
    "并按0<=creditFen<=priceFen、dueFen=priceFen-creditFen重算金额。任何变化拒绝并要求重新报价，不接受客户端金额。"
)
create_order = paths[APP + "/orders"]["post"]
create_order["description"] = "重核报价并创建正应付订单；仅dueFen>0。" + quote_confirmation_guard + "零补款不得创建订单或支付尝试，返回409并引导独立upgrade。"
create_order["x-static-cases"] = [
    {"case": "正补款报价确认创建订单", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "报价属于当前主体，expectedAccessRevision=quote.access_revision=当前守卫revision=7，来源/在途抵扣与金额重核一致且dueFen>0",
     "expect": "创建同一报价范围的应付订单；不另造抵扣或接受客户端金额"},
    {"case": "零补款误走订单", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "归属、三重revision及来源重核均有效，但dueFen=0",
     "expect": "拒绝createOrder；不创建订单或支付尝试；引导createUpgrade"},
    {"case": "revision或报价归属变化拒绝", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "6"},
     "given": "报价不属于当前主体，或expectedAccessRevision、quote.access_revision、当前守卫revision任一不相等",
     "expect": "拒绝且不创建订单；重新取得报价与确认，不泄露他人报价"},
    {"case": "抵扣来源或在途金额变化拒绝", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "来源归属/净实付/已分配/在途抵扣或revision变化，或重算不满足金额关系",
     "expect": "拒绝并不创建订单；重新报价，不重复使用抵扣"},
]
create_upgrade = paths[APP + "/upgrades"]["post"]
create_upgrade["description"] = "重核并创建零补款升级；仅dueFen=0。" + quote_confirmation_guard + "正补款不得直接创建升级，必须先走订单并由渠道核实后交付。"
create_upgrade["x-static-cases"] = [
    {"case": "零补款报价确认创建升级", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "报价属于当前主体，expectedAccessRevision=quote.access_revision=当前守卫revision=7，来源/在途抵扣与金额重核一致且dueFen=0",
     "expect": "创建零补款升级并原子抵扣；不创建订单或支付尝试"},
    {"case": "正补款误走升级", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "归属、三重revision及来源重核均有效，但dueFen>0",
     "expect": "拒绝createUpgrade；不直接交付；引导createOrder并等待渠道核实"},
    {"case": "revision或报价归属变化拒绝", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "6"},
     "given": "报价不属于当前主体，或expectedAccessRevision、quote.access_revision、当前守卫revision任一不相等",
     "expect": "拒绝且不创建升级或抵扣；重新取得报价与确认，不泄露他人报价"},
    {"case": "抵扣来源或在途金额变化拒绝", "schemaValid": True,
     "request": {"quoteId": "123e4567-e89b-42d3-a456-426614174000", "expectedAccessRevision": "7"},
     "given": "来源归属/净实付/已分配/在途抵扣或revision变化，或重算不满足金额关系",
     "expect": "拒绝且不创建升级或抵扣；重新报价，不重复使用抵扣"},
]
paths[APP + "/upgrades"]["post"]["description"] += (
    "；Upgrade必须完整返回目标productRevisionId、priceFen、currency、promise与contentKeys，"
    "以及服务端重核的creditFen/dueFen；零补款不得返回orderId，交付时必须返回grantId。"
)

restriction_operations = {
    "logoutPlayer", "completeReset", "requestDeletion", "confirmDeletion",
    "adminChangeGameState", "adminExecutePlan",
}
for item in paths.values():
    for op in item.values():
        if op["operationId"] not in restriction_operations:
            continue
        op["x-restriction-completion"] = "SD2：涉及限制时，业务限制/操作/事件/头/必要outbox同一事务提交后才报告该限制完成"
        op["description"] += (
            "；涉及注销、撤会话、撤权或暂停时按SD2使用xj_play同库事务。"
            "对应限制变更及APPLIED操作/事件/头/必要outbox须同一事务提交；"
            "不再使用独立PREPARED或跨库补写。提交未明返回503，"
            "按原Idempotency-Key查证/重试，不换键另做；旧快照缺行不能证明未执行。"
            "业务对象仍按自身state表达，注销PROCESSING或售后受理"
            "不等于游戏分类清理、现金退款或权益调整全部完成。"
        )
        op["responses"]["503"]["description"] += "；限制提交可能未明，不能推断未执行，复用原键查证"
        if op["operationId"] == "completeReset":
            op["description"] += (
                "；重置的一次性令牌消费、口令更新、会话撤销与限制记录同一本地事务提交。"
                "重试先以原动作、原键及可信请求绑定核对原持久结果，"
                "不能仅因原令牌已消费而丢失已成功结果，也不能只凭请求键读取他人结果；"
                "限制计划、事件与日志不得包含口令、原始令牌或密码哈希。"
            )

# Native notification surfaces preserve channel-specific acknowledgement; no Cookie/CSRF wrapper.
schema("AlipayNotice", {
    "notify_time": text(64), "notify_type": text(64), "notify_id": text(128),
    "app_id": text(128), "charset": text(32), "version": text(32),
    "sign_type": enum("RSA2"), "sign": text(2048), "out_trade_no": text(64),
    "trade_no": text(128), "trade_status": enum("WAIT_BUYER_PAY", "TRADE_CLOSED", "TRADE_SUCCESS", "TRADE_FINISHED"),
    "total_amount": text(32, pattern="^[0-9]+\\.[0-9]{2}$"), "seller_id": text(128),
}, ["app_id", "sign_type", "sign", "out_trade_no", "trade_no", "trade_status", "total_amount", "seller_id"])
# Channel additions are allowed only here, kept in original verification input then explicitly projected.
S["AlipayNotice"]["additionalProperties"] = {"type": "string"}
schema("WechatNotice", {"id": text(128), "create_time": TIME, "event_type": text(128),
                        "resource_type": text(128), "summary": text(1000),
                        "resource": obj({"algorithm": {"const": "AEAD_AES_256_GCM"}, "ciphertext": text(1048576),
                                         "associated_data": text(1024, 0), "nonce": text(128),
                                         "original_type": text(128)}, ["algorithm", "ciphertext", "nonce"])})
for channel in ("alipay", "wechat"):
    for kind in ("payments", "refunds") if channel == "wechat" else ("payments",):
        notice_name = "AlipayNotice" if channel == "alipay" else "WechatNotice"
        media = "application/x-www-form-urlencoded" if channel == "alipay" else "application/json"
        success = {"type": "string", "const": "success"} if channel == "alipay" else EMPTY
        op = {
            "operationId": channel + kind.title() + "Notify", "summary": f"{channel} {kind}原生通知",
            "security": [], "tags": ["渠道通知"],
            "description": "保留原始请求验签；校验商户/应用/原订单/金额/币种/状态；落盘去重与可靠后续任务后才确认。未知或存储故障按渠道失败应答并查证",
            "parameters": [] if channel == "alipay" else [
                {"name": h, "in": "header", "required": True, "schema": text(4096)}
                for h in ("Wechatpay-Serial", "Wechatpay-Signature", "Wechatpay-Timestamp", "Wechatpay-Nonce")],
            "requestBody": {"required": True, "content": {media: {"schema": ref(notice_name)}}},
            "responses": {
                "200" if channel == "alipay" else "204": {
                    "description": "渠道原生成功应答；微信204无正文",
                    **({"content": {"text/plain": {"schema": success}}} if channel == "alipay" else {})},
                "400": {"description": "签名/数据校验拒绝；按渠道失败协议"},
                "500": {"description": "持久处理失败；不确认成功，等待重试并查单"}},
            "x-authentication": "CHANNEL_SIGNATURE；独立于玩家/管理员会话",
            "x-runtime-status": "设计，原生字段以官方适配资料核定",
        }
        if channel == "alipay":
            op["responses"]["200"]["description"] += "；拒绝或处理失败不得输出success，可按官方返回failure"
        paths.setdefault(f"/app-api/xj/v1/{kind}/notifications/{channel}", {})["post"] = op

document = {
    "openapi": "3.1.1",
    "info": {"title": "间隙PLAY 平台接口架构草案", "version": "0.1.0",
             "description": "2026-10-25。设计规格，未运行。覆盖玩家/平台后台/双支付通知；既有system/infra独立保留，不冒称已完成对接。"},
    "servers": [{"url": "https://platform.invalid", "description": "文档占位，非已部署域名"}],
    "paths": paths,
    "components": {
        "securitySchemes": {
            "playerSession": {"type": "apiKey", "in": "cookie", "name": "__Host-xj-session",
                              "description": "宿主HttpOnly/Secure/SameSite，玩家与匿名由服务端区分；每次校验撤销代次"},
            "adminBearer": {"type": "http", "scheme": "bearer",
                            "description": "适配既有system，token不意味着已具对象权限；不承诺JWT"},
        },
        "schemas": S,
    },
    "x-limits-status": "事件单批20/资源上传配额/包大小为架构建议或待资源核准；不改变已确认产品每页12与存档1MiB",
}
(BASE / "05-资料/平台OpenAPI-V0.1.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
# Standalone JSON Schema document rewrites local component references.
event_doc = {"$schema": "https://json-schema.org/draft/2020-12/schema",
             "$id": "https://schema.invalid/xj/events/1.0", "title": "固定31事件及可信来源",
             "$defs": {name: value for name, value in S.items() if name.startswith("Event") or name == "BusinessRef"},
             "$ref": "#/$defs/Event"}
raw = json.dumps(event_doc, ensure_ascii=False, indent=2).replace("#/components/schemas/", "#/$defs/")
(BASE / "05-资料/平台事件Schema-V0.1.json").write_text(raw + "\n")
print(f"已生成OpenAPI设计：{sum(len(v) for v in paths.values())}个操作/{len(S)}个schema，固定{len(events)}事件")
