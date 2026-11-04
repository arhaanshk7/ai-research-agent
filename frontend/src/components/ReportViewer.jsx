import Markdown from "./Markdown"


function ReportViewer({ markdown, meta }) {

  const title = meta?.title || ""
  const subtitle = meta?.subtitle || ""
  const category = meta?.category || "Research Report"

  let body = markdown || ""

  // The header already shows the title and subtitle, so drop them from the body
  if (title) {

   body = body.replace(/^#\s+.*\n?/, "")
   body = body.replace(/^\*+.*\n?/, "")
   body = body.trimStart()
  }

  const date = new Date()
    .toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "long",
      year: "numeric"
    })
    .toUpperCase()

  const badges = [category, "Evidence-Based", "With Sources"]


  return (

    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">


      {/* Report eyebrow */}
      <div className="border-b border-slate-200 bg-slate-50 px-6 py-3 sm:px-10">

        <span className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">

          AI Research Report · {date}

        </span>

      </div>


      <div className="px-6 py-8 sm:px-10">


        {/* Title block */}
        {title && (

          <header className="mb-8 border-b border-slate-200 pb-6">

            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">

              {title}

            </h1>

            {subtitle && (

              <p className="mt-3 text-lg italic leading-7 text-slate-500">

                {subtitle}

              </p>

            )}

            <div className="mt-5 flex flex-wrap gap-2">

              {badges.map((badge) => (

                <span
                  key={badge}
                  className="rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold tracking-wide text-slate-600"
                >

                  {badge}

                </span>

              ))}

            </div>

          </header>

        )}


        {/* Report body */}
        <Markdown>{body}</Markdown>


      </div>

    </div>

  )

}


export default ReportViewer
