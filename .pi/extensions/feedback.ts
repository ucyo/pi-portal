import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

/**
 * Pi Portal Feedback Extension
 * 
 * Stores user feedback (ratings and comments) for assistant messages.
 * Feedback is persisted in the session as CustomEntry, so it travels
 * with the session file.
 * 
 * Usage via RPC:
 *   {"type": "prompt", "message": "/feedback {\"targetTimestamp\":1234567890,\"rating\":1}"}
 *   {"type": "prompt", "message": "/feedback {\"targetTimestamp\":1234567890,\"rating\":-1,\"comment\":\"Wrong answer\"}"}
 * 
 * Rating values:
 *   -1 = negative (thumbs down)
 *    0 = neutral (no rating / cleared)
 *    1 = positive (thumbs up)
 */

interface FeedbackData {
  targetTimestamp: number;
  rating: -1 | 0 | 1;
  comment?: string | null;
}

export default function (pi: ExtensionAPI) {
  pi.registerCommand("feedback", {
    description: "Save feedback for a message (rating: -1, 0, or 1)",
    handler: async (args, ctx) => {
      if (!args || args.trim() === "") {
        ctx.ui.notify("Usage: /feedback {\"targetTimestamp\":123,\"rating\":1}", "error");
        return;
      }

      try {
        const data: FeedbackData = JSON.parse(args);

        // Validate required fields
        if (typeof data.targetTimestamp !== "number") {
          ctx.ui.notify("Missing or invalid targetTimestamp", "error");
          return;
        }

        if (![-1, 0, 1].includes(data.rating)) {
          ctx.ui.notify("Rating must be -1, 0, or 1", "error");
          return;
        }

        // Clear comment if rating is not negative
        const comment = data.rating === -1 ? (data.comment ?? null) : null;

        // Persist feedback as CustomEntry
        pi.appendEntry("pi-portal-feedback", {
          targetTimestamp: data.targetTimestamp,
          rating: data.rating,
          comment: comment,
          timestamp: Date.now()
        });

        const ratingLabel = data.rating === 1 ? "👍" : data.rating === -1 ? "👎" : "cleared";
        ctx.ui.notify(`Feedback saved: ${ratingLabel}`, "info");

      } catch (error) {
        ctx.ui.notify(`Invalid JSON: ${error}`, "error");
      }
    }
  });

  // Command to list all feedback in current session
  pi.registerCommand("feedback-list", {
    description: "List all feedback in current session",
    handler: async (_args, ctx) => {
      const entries = ctx.sessionManager.getEntries();
      const feedbackEntries = entries.filter(
        (e) => e.type === "custom" && e.customType === "pi-portal-feedback"
      );

      if (feedbackEntries.length === 0) {
        ctx.ui.notify("No feedback recorded in this session", "info");
        return;
      }

      let summary = `Found ${feedbackEntries.length} feedback entries:\n`;
      for (const entry of feedbackEntries) {
        const data = entry.data as {
          targetTimestamp: number;
          rating: number;
          comment?: string | null;
        };
        const icon = data.rating === 1 ? "👍" : data.rating === -1 ? "👎" : "⚪";
        summary += `  ${icon} ts:${data.targetTimestamp}`;
        if (data.comment) {
          summary += ` - "${data.comment}"`;
        }
        summary += "\n";
      }

      ctx.ui.notify(summary.trim(), "info");
    }
  });
}
