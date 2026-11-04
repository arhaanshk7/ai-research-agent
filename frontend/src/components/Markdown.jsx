import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"


// Turn inline citations like [1] into links that jump to #ref-1
function linkifyCitations(markdown) {
  return markdown.replace(
    /\[(\d{1,2})\](?!\()/g,
    (_match, n) => `[${n}](#ref-${n})`
  )
}


const components = {

  h1: ({ node, children, ...props }) => (
    <h1
      className="mt-2 mb-4 text-3xl font-bold tracking-tight text-slate-900"
      {...props}
    >
      {children}
    </h1>
  ),

  h2: ({ node, children, ...props }) => (
    <h2
      className="mt-10 mb-4 border-b border-slate-200 pb-2 text-2xl font-bold tracking-tight text-slate-900"
      {...props}
    >
      {children}
    </h2>
  ),

  h3: ({ node, children, ...props }) => (
    <h3
      className="mt-8 mb-3 text-xl font-semibold text-slate-900"
      {...props}
    >
      {children}
    </h3>
  ),

  h4: ({ node, children, ...props }) => (
    <h4
      className="mt-6 mb-2 text-base font-semibold text-slate-900"
      {...props}
    >
      {children}
    </h4>
  ),

  p: ({ node, children, ...props }) => (
    <p
      className="my-4 text-[15px] leading-7 text-slate-700"
      {...props}
    >
      {children}
    </p>
  ),

  a: ({ node, href, children, ...props }) => {

    const isCitation = typeof href === "string" && href.startsWith("#ref-")
    const isExternal = typeof href === "string" && /^https?:/.test(href)

    return (
      <a
        href={href}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noreferrer" : undefined}
        className={
          isCitation
            ? "mx-0.5 align-super text-[11px] font-semibold text-blue-600 no-underline hover:text-blue-800 hover:underline"
            : "font-medium text-blue-600 underline-offset-2 hover:underline"
        }
        {...props}
      >
        {children}
      </a>
    )
  },

  ul: ({ node, children, ...props }) => (
    <ul
      className="my-4 list-disc space-y-1.5 pl-6 text-[15px] leading-7 text-slate-700"
      {...props}
    >
      {children}
    </ul>
  ),

  ol: ({ node, children, ...props }) => (
    <ol
      className="my-4 list-decimal space-y-1.5 pl-6 text-[15px] leading-7 text-slate-700"
      {...props}
    >
      {children}
    </ol>
  ),

  li: ({ node, children, ...props }) => {

    const first = Array.isArray(children) ? children[0] : children
    const href = first?.props?.href

    // Reference entries get an anchor id so citations can jump to them
    const id =
      typeof href === "string" && href.startsWith("#ref-")
        ? href.slice(1)
        : undefined

    return (
      <li
        id={id}
        className={
          id
            ? "my-3 scroll-mt-6 text-[15px] leading-7 text-slate-700"
            : "text-[15px] leading-7 text-slate-700"
        }
        {...props}
      >
        {children}
      </li>
    )
  },

  blockquote: ({ node, children, ...props }) => (
    <blockquote
      className="my-6 rounded-r-xl border-l-4 border-blue-400 bg-blue-50 px-5 py-4"
      {...props}
    >
      {children}
    </blockquote>
  ),

  table: ({ node, children, ...props }) => (
    <div className="my-6 overflow-x-auto">
      <table
        className="w-full border-collapse text-left text-sm"
        {...props}
      >
        {children}
      </table>
    </div>
  ),

  th: ({ node, children, ...props }) => (
    <th
      className="border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-900"
      {...props}
    >
      {children}
    </th>
  ),

  td: ({ node, children, ...props }) => (
    <td
      className="border border-slate-200 px-4 py-2.5 text-sm text-slate-700"
      {...props}
    >
      {children}
    </td>
  ),

  strong: ({ node, children, ...props }) => (
    <strong className="font-semibold text-slate-900" {...props}>
      {children}
    </strong>
  ),

  hr: ({ node, ...props }) => (
    <hr className="my-8 border-slate-200" {...props} />
  ),

  pre: ({ node, children, ...props }) => (
    <pre
      className="my-6 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-4"
      {...props}
    >
      {children}
    </pre>
  ),

  code: ({ node, children, ...props }) => (
    <code
      className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[13px] text-slate-800"
      {...props}
    >
      {children}
    </code>
  ),
}


function Markdown({ children, className = "" }) {

  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {linkifyCitations(children || "")}
      </ReactMarkdown>
    </div>
  )
}


export default Markdown
