
import { useState } from "react"
import { startResearch } from "../services/api"


function ResearchInput({
  setThreadId,
  setReport,
  setMeta,
  setReviewReady,
  isSearching,
  setIsSearching,
  setApproved,
}) {

  const [topic, setTopic] = useState("")


  async function handleResearch() {

    const query = topic.trim()

    if (!query || isSearching) {
      return
    }


    // Clear previous research
    setReport("")
    setMeta({})
    setReviewReady(false)
    setApproved(false)
    setIsSearching(true)

    setTopic("")


    try {

      await startResearch(

        query,


      // Receive report chunks
      (chunk) => {
        setReport(prev => prev + chunk)
      },


      // Receive report metadata
      (meta) => {
        setMeta(meta)
      },


      // Receive thread ID
      (threadId) => {
        setThreadId(threadId)
      },


      // Research + streaming finished
      (finalReport, finalMeta) => {

        if (finalReport) {
          setReport(finalReport)
        }

        if (finalMeta) {
          setMeta(finalMeta)
        }

        setReviewReady(true)
      }

      )

    } catch (error) {

      console.error("Research failed:", error)

    } finally {

      setIsSearching(false)
    }
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
          disabled={isSearching}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200 disabled:cursor-not-allowed disabled:bg-gray-100"
        />


        <button
          onClick={handleResearch}
          disabled={isSearching || !topic.trim()}
          className="rounded-lg bg-gray-900 px-6 py-3 font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSearching ? "Researching..." : "Start Research"}
        </button>

      </div>

    </div>
  )
}


export default ResearchInput

