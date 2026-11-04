
import axios from "axios"

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
})


// -------------------------
// Start Research
// -------------------------

export const startResearch = async (
  topic,
  onChunk,
  onMeta,
  onThreadId,
  onReviewReady
) => {

  const response = await fetch("http://127.0.0.1:8000/research", {
    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      topic: topic
    })
  })


  const reader = response.body.getReader()

  const decoder = new TextDecoder()

  let buffer = ""


  while (true) {

    const { value, done } = await reader.read()

    if (done) {
      break
    }


    buffer += decoder.decode(value, {
      stream: true
    })


    const lines = buffer.split("\n")

    buffer = lines.pop()


    for (const line of lines) {

      if (!line.trim()) {
        continue
      }


      const data = JSON.parse(line)


      // -------------------------
      // Thread ID
      // -------------------------

      if (data.type === "thread_id") {

        onThreadId(data.thread_id)

      }


      // -------------------------
      // Report chunk
      // -------------------------

      else if (data.type === "report_chunk") {

        onChunk(data.content)

      }


      // -------------------------
      // Report metadata (title, subtitle, category)
      // -------------------------

      else if (data.type === "report_meta") {

        onMeta(data.meta)

      }


      // -------------------------
      // Report finished
      // -------------------------

      else if (data.type === "review_ready") {

        onReviewReady(data.report, data.meta)

      }

    }

  }
}

// -------------------------
// Human Review
// -------------------------

export const submitReview = async (
  threadId,
  approved,
  feedback = ""
) => {

  const response = await API.post("/review", {

    thread_id: threadId,
    approved: approved,
    feedback: feedback

  })

  return response.data
}


// -------------------------
// Follow-up Question
// -------------------------

export const askFollowUp = async (
  threadId,
  question,
  onChunk,
  onComplete
) => {

  const response = await fetch("http://127.0.0.1:8000/follow-up", {
    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      thread_id: threadId,
      question: question
    })
  })

  if (!response.ok) {
    throw new Error("Follow-up request failed")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  let buffer = ""

  while (true) {

    const { value, done } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split("\n")

    buffer = lines.pop()

    for (const line of lines) {

      if (!line.trim()) {
        continue
      }

      const data = JSON.parse(line)

      if (data.type === "followup_chunk") {

        onChunk(data.content)

      }

    }
  }

  onComplete()
}
