
import { useState } from "react"
import { startResearch } from "../services/api"


function ResearchInput({ setThreadId, setReport, setSources, setReviewReady }) {

  const [topic, setTopic] = useState("")


  async function handleResearch() {

    if (!topic.trim()) {
      return
    }


    // Clear previous research
    setReport("")
    setSources([])
    setReviewReady(false)

    setTopic("")


    await startResearch(

      topic,


      // Receive report chunks
      (chunk) => {
        setReport(prev => prev + chunk)
      },


      // Receive sources
      (source) => {
        setSources(prev => [...prev, source])
      },


      // Receive thread ID
      (threadId) => {
        setThreadId(threadId)
      },


      // Research + streaming finished
      () => {
        setReviewReady(true)
      }

    )
  }


  return (
    <div>

      <h2 className="text-2xl font-semibold text-gray-900">
        Start Your Research
      </h2>

      <p className="mt-1 text-sm text-gray-500">
        Enter a topic and let the AI research it for you.
      </p>


      <div className="mt-5 flex flex-col gap-3 sm:flex-row">

        <input
          type="text"
          placeholder="Enter your research topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
        />


        <button
          onClick={handleResearch}
          className="rounded-lg bg-gray-900 px-6 py-3 font-medium text-white transition hover:bg-gray-700"
        >
          Start Research
        </button>

      </div>

    </div>
  )
}


export default ResearchInput

