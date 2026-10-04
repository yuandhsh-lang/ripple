// SPDX-License-Identifier: Apache-2.0
export type ErrorCode = "PERMISSION_DENIED" | "USER_DECLINED" | "STATE_STALE"
  | "EXECUTION_FAILED" | "VERIFICATION_FAILED" | "DEPENDENCY_UNAVAILABLE" | "INVALID_INPUT";

export class WorkflowError extends Error {
  readonly code: ErrorCode;
  readonly retryable: boolean;
  readonly outcomeUnknown: boolean;

  constructor(code: ErrorCode, message: string, retryable = false, outcomeUnknown = false) {
    super(message);
    this.name = "WorkflowError";
    this.code = code;
    this.retryable = retryable;
    this.outcomeUnknown = outcomeUnknown;
  }
}

export function workflowError(error: unknown, fallback: ErrorCode): WorkflowError {
  if (error instanceof WorkflowError) return error;
  return new WorkflowError(fallback, error instanceof Error ? error.message : "操作失败，结果未验证。",
    fallback === "DEPENDENCY_UNAVAILABLE" || fallback === "EXECUTION_FAILED", fallback === "EXECUTION_FAILED");
}
