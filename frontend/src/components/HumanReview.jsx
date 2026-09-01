import { useState } from "react"
import { submitReview } from "../services/api"

function HumanReview({ threadId, setReport, setApproved }) {

  const [feedback, setFeedback] = useState("")
  
  if (!threadId) {
    return null
  }

  async function handleApprove() {

    await submitReview(threadId, true, "")

    setApproved(true)
  }

  async function handleReject() {

    const data = await submitReview(
      threadId,
      false,
      feedback
    )

    if (data.report) {
      setReport(data.report)
    }

    setFeedback("")
  }

  return (
    <div>

      <div className="flex items-center justify-between">

        <div>
          <h2 className="text-2xl font-semibold text-gray-900">
            Human Review
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Review the report before continuing.
          </p>
        </div>

      </div>


      <div className="mt-6 flex flex-col gap-4">

        <button
          onClick={handleApprove}
          className="rounded-lg bg-green-600 px-5 py-3 font-medium text-white transition hover:bg-green-700"
        >
          Approve Report
        </button>


        <div>

          <label className="mb-2 block text-sm font-medium text-gray-700">
            Request changes
          </label>

          <textarea
            placeholder="Tell the AI what should be improved..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows="4"
            className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
          />

        </div>


        <button
          onClick={handleReject}
          disabled={!feedback.trim()}
          className="rounded-lg border border-gray-300 px-5 py-3 font-medium text-gray-800 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Request Changes
        </button>

      </div>

    </div>
  )
}

export default HumanReview