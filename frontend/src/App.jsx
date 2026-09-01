
import { useState } from "react";
import ResearchInput from "./components/ResearchInput";
import HumanReview from "./components/HumanReview";
import FollowUpChat from "./components/FollowUpChat";


function App() {

  const [threadId, setThreadId] = useState("");

  const [report, setReport] = useState("");

  const [sources, setSources] = useState([]);

  const [reviewReady, setReviewReady] = useState(false);

  const [approved, setApproved] = useState(false);


  return (

    <div className="min-h-screen bg-slate-100 text-slate-900">


      {/* Header */}

      <header className="border-b border-slate-200 bg-white">

        <div className="mx-auto max-w-5xl px-6 py-8">

          <div className="flex items-center gap-4">


            {/* Logo */}

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">

              <span className="text-xl font-bold">
                AI
              </span>

            </div>


            {/* Title */}

            <div>

              <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                AI Research Agent
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Research, review, and ask follow-up questions
              </p>

            </div>

          </div>

        </div>

      </header>



      {/* Main Content */}

      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">


        {/* Research Input */}

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">

          <ResearchInput
            setThreadId={setThreadId}
            setReport={setReport}
            setSources={setSources}
            setReviewReady={setReviewReady}
          />

        </section>



        {/* Research Report */}

        {report && (

          <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">


            <div className="mb-5 flex items-start justify-between">

              <div>

                <h2 className="text-2xl font-bold text-slate-900">
                  Research Report
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Generated research based on your topic
                </p>

              </div>


              <div className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">

                {reviewReady ? "Completed" : "Generating..."}

              </div>

            </div>



            {/* Report */}

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

              <div className="whitespace-pre-wrap text-[15px] leading-7 text-slate-700">

                {report}

              </div>



              {/* Sources */}

              {sources.length > 0 && (

                <div className="mt-8 border-t border-slate-200 pt-6">

                  <h3 className="mb-3 text-lg font-semibold text-slate-900">
                    Sources
                  </h3>


                  <div className="space-y-2">

                    {sources.map((source, index) => (

                      <div
                        key={index}
                        className="text-sm leading-6 text-slate-600"
                      >

                        {source}

                      </div>

                    ))}

                  </div>

                </div>

              )}

            </div>

          </section>

        )}



        {/* Human Review */}

        {reviewReady && !approved && threadId && (

          <section className="mb-8 rounded-2xl border border-amber-200 bg-white p-6 shadow-sm sm:p-8">


            <div className="mb-6">

              <div className="flex items-center gap-3">


                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 text-amber-700">

                  👤

                </div>


                <div>

                  <h2 className="text-xl font-semibold text-slate-900">
                    Human Review
                  </h2>

                  <p className="text-sm text-slate-500">
                    Review the research before continuing.
                  </p>

                </div>

              </div>

            </div>


            <HumanReview
              threadId={threadId}
              setReport={setReport}
              setApproved={setApproved}
            />

          </section>

        )}



        {/* Follow Up Chat */}

        {approved && (

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">


            <div className="mb-6">

              <div className="flex items-center gap-3">


                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white">

                  💬

                </div>


                <div>

                  <h2 className="text-xl font-semibold text-slate-900">
                    Follow-up Questions
                  </h2>

                  <p className="text-sm text-slate-500">
                    Ask the research agent anything about the report.
                  </p>

                </div>

              </div>

            </div>


            <FollowUpChat
              threadId={threadId}
            />

          </section>

        )}

      </main>



      {/* Footer */}

      <footer className="border-t border-slate-200 bg-white">

        <div className="mx-auto max-w-5xl px-6 py-6 text-center text-sm text-slate-500">

          AI Research Agent · Powered by LangGraph

        </div>

      </footer>

    </div>

  );

}


export default App;

