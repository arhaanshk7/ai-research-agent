import { useState } from "react"
import { askFollowUp } from "../services/api"
import Markdown from "./Markdown"


function FollowUpChat({ threadId }) {

  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)


  async function handleSubmit() {

    if (!question.trim()) {
      return
    }

    setAnswer("")
    setLoading(true)

    const currentQuestion = question

    setQuestion("")

    try {

      await askFollowUp(
        threadId,
        currentQuestion,

        // Receive every streamed chunk
        (chunk) => {

          setAnswer(prev => prev + chunk)

        },

        // Streaming finished
        () => {

          setLoading(false)

        }
      )

    } catch (error) {

      console.error(error)
      setLoading(false)

    }
  }


  return (

    <div>

      {/* Question input */}

      <div className="flex flex-col gap-3 sm:flex-row">

        <input
          type="text"
          placeholder="Ask a follow-up question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="rounded-lg bg-gray-900 px-6 py-3 font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
        >

          {loading ? "Thinking..." : "Ask"}

        </button>

      </div>


      {/* Answer */}

      {answer && (

        <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-5">

          <h3 className="mb-3 text-lg font-semibold text-slate-900">
            Answer
          </h3>

          <Markdown>{answer}</Markdown>

        </div>

      )}

    </div>

  )
}


export default FollowUpChat