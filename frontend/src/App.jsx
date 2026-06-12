import React, { useState } from "react";
import axios from "axios";

const G3 = "http://localhost:9000";
const G1 = "http://localhost:8000";

const BLOOM_COLORS = {
  remember: "bg-blue-100 text-blue-800",
  understand: "bg-green-100 text-green-800",
  apply: "bg-yellow-100 text-yellow-800",
  analyze: "bg-orange-100 text-orange-800",
  evaluate: "bg-red-100 text-red-800",
  create: "bg-purple-100 text-purple-800",
};

const cellColor = (v) =>
  v === 3 ? "bg-green-600 text-white"
  : v === 2 ? "bg-orange-400 text-white"
  : v === 1 ? "bg-yellow-200 text-yellow-900"
  : "bg-white text-gray-400";

const levelColor = (l) =>
  l === 3 ? "bg-green-600 text-white"
  : l === 2 ? "bg-orange-400 text-white"
  : l === 1 ? "bg-yellow-300 text-yellow-900"
  : "bg-red-500 text-white";

const DEFAULT_FORM = {
  course_name: "",
  course_code: "",
  course_description: "",
  num_units: 5,
  credits: 4,
  ltp: "3:1:0",
  university_name: "G.B. Pant Institute of Engineering and Technology, Pauri Garhwal",
  programme: "btech",
  education_level: "undergraduate",
  branch: "Computer Science and Engineering",
  year_of_study: 2,
  semester: 3,
  programme_name: "",
  programme_description: "",
};

const DEFAULT_QUESTIONS = [
  { id: "q1", name: "Unit Test 1", max_marks: 20, co_id: "CO1" },
  { id: "q2", name: "Assignment 1", max_marks: 10, co_id: "CO2" },
  { id: "q3", name: "End Sem Q1", max_marks: 20, co_id: "CO3" },
];

const DEFAULT_STUDENTS = [
  { student_id: "S001", student_name: "", marks: {} },
  { student_id: "S002", student_name: "", marks: {} },
  { student_id: "S003", student_name: "", marks: {} },
];

const DEFAULT_ATTAIN = {
  target_score_percent: 60,
  threshold_l1: 50,
  threshold_l2: 60,
  threshold_l3: 70,
};

const LOADING_STEPS = [
  "Generating Course Outcomes and Units (AI is thinking...)",
  "Generating Programme Outcomes POs PSOs PEOs...",
  "Computing CO-PO Mapping...",
  "Computing CO-PSO and PO-PEO Mapping...",
  "Computing Semester Plan...",
  "Calculating Attainment Levels...",
];

// ─── Shared small components ──────────────────────────────────────────────────

function Field({ label, children, required }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      {children}
    </label>
  );
}

const inputCls =
  "mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500";

function MatrixTable({ rowIds, colIds, matrix, rowLabel }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-blue-50">
          <tr>
            <th className="px-3 py-2 text-left font-semibold text-blue-900">{rowLabel}</th>
            {colIds.map((c) => (
              <th key={c} className="px-3 py-2 text-center font-semibold text-blue-900">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rowIds.map((r) => (
            <tr key={r} className="border-t border-gray-100">
              <td className="px-3 py-2 font-medium text-gray-800">{r}</td>
              {colIds.map((c) => {
                const v = matrix?.[r]?.[c] ?? 0;
                return (
                  <td key={c} className="px-1 py-1 text-center">
                    <span className={`inline-block w-8 rounded py-1 text-xs font-semibold ${cellColor(v)}`}>
                      {v > 0 ? v : "–"}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Legend() {
  return (
    <div className="mt-3 flex flex-wrap gap-4 text-xs text-gray-600">
      <span><span className="mr-1 inline-block h-3 w-3 rounded bg-white align-middle ring-1 ring-gray-300" /> – No mapping</span>
      <span><span className="mr-1 inline-block h-3 w-3 rounded bg-yellow-200 align-middle" /> 1 Low</span>
      <span><span className="mr-1 inline-block h-3 w-3 rounded bg-orange-400 align-middle" /> 2 Medium</span>
      <span><span className="mr-1 inline-block h-3 w-3 rounded bg-green-600 align-middle" /> 3 High</span>
    </div>
  );
}

// ─── PAGE 1: Faculty form ─────────────────────────────────────────────────────

function FormPage({ onGenerated }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [attain, setAttain] = useState(DEFAULT_ATTAIN);
  const [questions, setQuestions] = useState(DEFAULT_QUESTIONS);
  const [students, setStudents] = useState(DEFAULT_STUDENTS);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const setNum = (k) => (e) => setForm({ ...form, [k]: Number(e.target.value) });

  const addQuestion = () =>
    setQuestions([...questions, { id: `q${questions.length + 1}`, name: "", max_marks: 10, co_id: "CO1" }]);
  const removeQuestion = (i) => setQuestions(questions.filter((_, idx) => idx !== i));
  const updateQuestion = (i, k, v) => {
    const qs = [...questions];
    qs[i] = { ...qs[i], [k]: k === "max_marks" ? Number(v) : v };
    setQuestions(qs);
  };

  const addStudent = () =>
    setStudents([...students, { student_id: `S${String(students.length + 1).padStart(3, "0")}`, student_name: "", marks: {} }]);
  const updateStudent = (i, k, v) => {
    const ss = [...students];
    ss[i] = { ...ss[i], [k]: v };
    setStudents(ss);
  };
  const updateMark = (i, qid, v) => {
    const ss = [...students];
    ss[i] = { ...ss[i], marks: { ...ss[i].marks, [qid]: v } };
    setStudents(ss);
  };

  const submit = async () => {
    setError("");
    if (!form.course_name || !form.course_description || !form.course_code) {
      setError("Course Name, Code and Description are required.");
      return;
    }
    setLoading(true);
    setStep(0);
    const ticker = setInterval(() => setStep((s) => Math.min(s + 1, LOADING_STEPS.length - 1)), 25000);
    try {
      const payload = {
        ...form,
        attainment_settings: { ...attain, questions, students },
      };
      const r = await axios.post(`${G3}/pipeline/generate`, payload, { timeout: 1200000 });
      onGenerated(payload, r.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Pipeline failed. Check that all services are running.");
    } finally {
      clearInterval(ticker);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-6">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
        <div className="text-center">
          <p className="text-lg font-semibold text-blue-900">Step {step + 1}/6</p>
          <p className="mt-1 text-gray-600">{LOADING_STEPS[step]}</p>
          <p className="mt-3 text-xs text-gray-400">AI generation can take several minutes. Please don't close this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      {error && <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div>}

      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h2 className="mb-4 text-lg font-semibold text-blue-900">1. Course Details</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="Course Name" required><input className={inputCls} value={form.course_name} onChange={set("course_name")} placeholder="Data Structures and Algorithms" /></Field>
          <Field label="Course Code" required><input className={inputCls} value={form.course_code} onChange={set("course_code")} placeholder="CS301" /></Field>
          <div className="md:col-span-2">
            <Field label="Course Description" required>
              <textarea className={inputCls} rows={3} value={form.course_description} onChange={set("course_description")} placeholder="Arrays, linked lists, stacks, queues, trees, graphs..." />
            </Field>
          </div>
          <Field label="Number of Units"><select className={inputCls} value={form.num_units} onChange={setNum("num_units")}>{[3,4,5,6].map(n=><option key={n} value={n}>{n}</option>)}</select></Field>
          <Field label="Credits"><select className={inputCls} value={form.credits} onChange={setNum("credits")}>{[2,3,4,5].map(n=><option key={n} value={n}>{n}</option>)}</select></Field>
          <Field label="LTP Pattern"><input className={inputCls} value={form.ltp} onChange={set("ltp")} /></Field>
        </div>
      </section>

      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h2 className="mb-4 text-lg font-semibold text-blue-900">2. Academic Details</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="md:col-span-2"><Field label="University Name"><input className={inputCls} value={form.university_name} onChange={set("university_name")} /></Field></div>
          <Field label="Programme"><select className={inputCls} value={form.programme} onChange={set("programme")}>{["btech","mtech","bsc","mca","diploma"].map(p=><option key={p} value={p}>{p}</option>)}</select></Field>
          <Field label="Education Level"><select className={inputCls} value={form.education_level} onChange={set("education_level")}><option value="undergraduate">undergraduate</option><option value="postgraduate">postgraduate</option></select></Field>
          <Field label="Branch"><input className={inputCls} value={form.branch} onChange={set("branch")} /></Field>
          <Field label="Year of Study"><select className={inputCls} value={form.year_of_study} onChange={setNum("year_of_study")}>{[1,2,3,4].map(n=><option key={n} value={n}>{n}</option>)}</select></Field>
          <Field label="Semester"><select className={inputCls} value={form.semester} onChange={setNum("semester")}>{[1,2,3,4,5,6,7,8].map(n=><option key={n} value={n}>{n}</option>)}</select></Field>
        </div>
      </section>

      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h2 className="mb-4 text-lg font-semibold text-blue-900">3. Programme Details</h2>
        <div className="grid grid-cols-1 gap-4">
          <Field label="Programme Name"><input className={inputCls} value={form.programme_name} onChange={set("programme_name")} placeholder="B.Tech Computer Science and Engineering" /></Field>
          <Field label="Programme Description"><textarea className={inputCls} rows={2} value={form.programme_description} onChange={set("programme_description")} placeholder="A four year undergraduate programme covering..." /></Field>
        </div>
      </section>

      <section className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h2 className="mb-1 text-lg font-semibold text-blue-900">4. Attainment Configuration</h2>
        <p className="mb-4 text-sm text-gray-500">Thresholds, assessment questions and student marks used to calculate CO/PO attainment levels.</p>

        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Field label="Target Score %"><input type="number" className={inputCls} value={attain.target_score_percent} onChange={(e)=>setAttain({...attain, target_score_percent:Number(e.target.value)})} /></Field>
          <Field label="Level 1 Threshold %"><input type="number" className={inputCls} value={attain.threshold_l1} onChange={(e)=>setAttain({...attain, threshold_l1:Number(e.target.value)})} /></Field>
          <Field label="Level 2 Threshold %"><input type="number" className={inputCls} value={attain.threshold_l2} onChange={(e)=>setAttain({...attain, threshold_l2:Number(e.target.value)})} /></Field>
          <Field label="Level 3 Threshold %"><input type="number" className={inputCls} value={attain.threshold_l3} onChange={(e)=>setAttain({...attain, threshold_l3:Number(e.target.value)})} /></Field>
        </div>

        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium text-gray-800">Assessment Questions</h3>
            <button onClick={addQuestion} className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700">+ Add Question</button>
          </div>
          <div className="space-y-2">
            {questions.map((q, i) => (
              <div key={q.id} className="flex items-center gap-2">
                <input className={inputCls + " flex-1"} placeholder="Question name" value={q.name} onChange={(e)=>updateQuestion(i,"name",e.target.value)} />
                <input type="number" className={inputCls + " w-24"} placeholder="Marks" value={q.max_marks} onChange={(e)=>updateQuestion(i,"max_marks",e.target.value)} />
                <select className={inputCls + " w-28"} value={q.co_id} onChange={(e)=>updateQuestion(i,"co_id",e.target.value)}>
                  {["CO1","CO2","CO3","CO4","CO5"].map(c=><option key={c} value={c}>{c}</option>)}
                </select>
                <button onClick={()=>removeQuestion(i)} className="rounded-md px-2 py-1 text-red-500 hover:bg-red-50" title="Remove">✕</button>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium text-gray-800">Student Marks</h3>
            <button onClick={addStudent} className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700">+ Add Student</button>
          </div>
          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full text-sm">
              <thead className="bg-blue-50">
                <tr>
                  <th className="px-3 py-2 text-left font-semibold text-blue-900">Student ID</th>
                  <th className="px-3 py-2 text-left font-semibold text-blue-900">Name</th>
                  {questions.map((q)=><th key={q.id} className="px-3 py-2 text-center font-semibold text-blue-900">{q.name || q.id}<div className="text-xs font-normal text-blue-700">/{q.max_marks}</div></th>)}
                </tr>
              </thead>
              <tbody>
                {students.map((s, i) => (
                  <tr key={s.student_id} className="border-t border-gray-100">
                    <td className="px-3 py-1.5 font-medium text-gray-700">{s.student_id}</td>
                    <td className="px-2 py-1.5"><input className={inputCls} value={s.student_name} onChange={(e)=>updateStudent(i,"student_name",e.target.value)} placeholder="Student name" /></td>
                    {questions.map((q)=>(
                      <td key={q.id} className="px-2 py-1.5">
                        <input type="number" className={inputCls + " w-20 text-center"} value={s.marks[q.id] ?? ""} onChange={(e)=>updateMark(i,q.id,e.target.value)} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="flex justify-end pb-12">
        <button onClick={submit} className="rounded-lg bg-blue-600 px-8 py-3 text-base font-semibold text-white shadow hover:bg-blue-700">
          Generate Syllabus
        </button>
      </div>
    </div>
  );
}

// ─── PAGE 2: Review ───────────────────────────────────────────────────────────

function ReviewPage({ formData, result, onApproved, onRejectedResult }) {
  const [tab, setTab] = useState(0);
  const [showReject, setShowReject] = useState(false);
  const [reason, setReason] = useState("");
  const [custom, setCustom] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const tabs = ["Course Outcomes", "CO-PO Matrix", "CO-PSO Matrix", "PO-PEO Matrix", "Semester Plan", "Attainment Levels"];

  const coIds  = result.cos.map((c) => c.co_id);
  const poIds  = result.pos.map((p) => p.po_id);
  const psoIds = result.psos.map((p) => p.pso_id);
  const peoIds = result.peos.map((p) => p.peo_id);

  const coStats = result.attainment?.co_stats || {};
  const poStats = result.attainment?.po_stats || {};
  const levelCounts = [3, 2, 1, 0].map((l) => Object.values(coStats).filter((s) => s.level === l).length);

  const approve = async () => {
    setBusy(true); setError("");
    try {
      const r = await axios.post(`${G3}/pipeline/approve`, formData, { timeout: 1200000 });
      onApproved(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally { setBusy(false); }
  };

  const reject = async () => {
    if (!reason.trim()) { setError("Rejection reason is required."); return; }
    setBusy(true); setError("");
    try {
      const r = await axios.post(`${G3}/pipeline/reject`, { ...formData, rejection_reason: reason, custom_prompt: custom || null }, { timeout: 1200000 });
      setShowReject(false); setReason(""); setCustom("");
      onRejectedResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally { setBusy(false); }
  };

  return (
    <div className="mx-auto max-w-5xl">
      {error && <div className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div>}

      <div className="mb-4 flex flex-wrap gap-1 rounded-lg bg-blue-50 p-1">
        {tabs.map((t, i) => (
          <button key={t} onClick={() => setTab(i)}
            className={`rounded-md px-4 py-2 text-sm font-medium ${tab === i ? "bg-white text-blue-900 shadow" : "text-blue-700 hover:bg-blue-100"}`}>
            {t}
          </button>
        ))}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        {tab === 0 && (
          <table className="min-w-full text-sm">
            <thead className="bg-blue-50"><tr>
              <th className="px-3 py-2 text-left font-semibold text-blue-900">CO ID</th>
              <th className="px-3 py-2 text-left font-semibold text-blue-900">Bloom Level</th>
              <th className="px-3 py-2 text-left font-semibold text-blue-900">CO Text</th>
            </tr></thead>
            <tbody>
              {result.cos.map((c) => (
                <tr key={c.co_id} className="border-t border-gray-100">
                  <td className="px-3 py-2 font-semibold text-gray-800">{c.co_id}</td>
                  <td className="px-3 py-2">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${BLOOM_COLORS[(c.bloom_level||"").toLowerCase()] || "bg-gray-100 text-gray-700"}`}>{c.bloom_level}</span>
                  </td>
                  <td className="px-3 py-2 text-gray-700">{c.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {tab === 1 && (<><MatrixTable rowIds={coIds} colIds={poIds} matrix={result.co_po_matrix} rowLabel="CO" /><Legend /></>)}
        {tab === 2 && (<><MatrixTable rowIds={coIds} colIds={psoIds} matrix={result.co_pso_matrix} rowLabel="CO" /><Legend /></>)}
        {tab === 3 && (<><MatrixTable rowIds={poIds} colIds={peoIds} matrix={result.po_peo_matrix} rowLabel="PO" /><Legend /></>)}

        {tab === 4 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {(result.semester_plan || []).length === 0 && <p className="text-gray-500">No semester plan available.</p>}
            {(result.semester_plan || []).map((s) => (
              <div key={s.semester} className="rounded-lg border border-gray-200 p-4">
                <p className="font-semibold text-blue-900">Semester {s.semester}</p>
                <ul className="mt-2 list-inside list-disc text-sm text-gray-700">
                  {s.courses.map((c) => <li key={c}>{c}</li>)}
                </ul>
                <p className="mt-2 text-xs text-gray-500">{s.credits} credits</p>
              </div>
            ))}
          </div>
        )}

        {tab === 5 && (
          <div className="space-y-8">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {[["COs at Level 3", levelCounts[0], "bg-green-600"], ["COs at Level 2", levelCounts[1], "bg-orange-400"], ["COs at Level 1", levelCounts[2], "bg-yellow-400"], ["COs at Level 0", levelCounts[3], "bg-red-500"]].map(([label, n, bg]) => (
                <div key={label} className="rounded-lg border border-gray-200 p-4 text-center">
                  <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold text-white ${bg}`}>{n}</div>
                  <p className="text-xs text-gray-600">{label}</p>
                </div>
              ))}
            </div>

            <div>
              <h3 className="mb-2 font-semibold text-gray-800">CO Attainment</h3>
              {Object.keys(coStats).length === 0 ? <p className="text-sm text-gray-500">No attainment data — add questions and student marks on the form page.</p> : (
                <table className="min-w-full text-sm">
                  <thead className="bg-blue-50"><tr>
                    <th className="px-3 py-2 text-left font-semibold text-blue-900">CO</th>
                    <th className="px-3 py-2 text-left font-semibold text-blue-900">Achievement %</th>
                    <th className="px-3 py-2 text-left font-semibold text-blue-900">Level</th>
                  </tr></thead>
                  <tbody>
                    {Object.values(coStats).map((s) => (
                      <tr key={s.co_id} className="border-t border-gray-100">
                        <td className="px-3 py-2 font-medium">{s.co_id}</td>
                        <td className="px-3 py-2">
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-40 rounded bg-gray-100"><div className="h-2 rounded bg-blue-500" style={{ width: `${Math.min(s.percentage, 100)}%` }} /></div>
                            <span className="text-xs text-gray-600">{s.percentage}%</span>
                          </div>
                        </td>
                        <td className="px-3 py-2"><span className={`rounded px-2 py-0.5 text-xs font-semibold ${levelColor(s.level)}`}>Level {s.level}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div>
              <h3 className="mb-2 font-semibold text-gray-800">PO Attainment</h3>
              {Object.keys(poStats).length === 0 ? <p className="text-sm text-gray-500">No PO attainment data.</p> : (
                <table className="min-w-full text-sm">
                  <thead className="bg-blue-50"><tr>
                    <th className="px-3 py-2 text-left font-semibold text-blue-900">PO</th>
                    <th className="px-3 py-2 text-left font-semibold text-blue-900">Attainment Score</th>
                  </tr></thead>
                  <tbody>
                    {Object.values(poStats).map((s) => (
                      <tr key={s.po_id} className="border-t border-gray-100">
                        <td className="px-3 py-2 font-medium">{s.po_id}</td>
                        <td className="px-3 py-2 text-gray-700">{s.attainment}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="my-8 flex justify-end gap-4 pb-12">
        <button onClick={() => setShowReject(true)} disabled={busy}
          className="rounded-lg bg-red-600 px-6 py-3 font-semibold text-white shadow hover:bg-red-700 disabled:opacity-50">
          Reject
        </button>
        <button onClick={approve} disabled={busy}
          className="rounded-lg bg-green-600 px-6 py-3 font-semibold text-white shadow hover:bg-green-700 disabled:opacity-50">
          {busy ? "Working..." : "Approve and Generate Full Syllabus"}
        </button>
      </div>

      {showReject && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="mb-4 text-lg font-semibold text-gray-900">Reject and Regenerate</h3>
            <Field label="Rejection Reason" required>
              <textarea className={inputCls} rows={3} value={reason} onChange={(e)=>setReason(e.target.value)} placeholder="Insufficient practical content..." />
            </Field>
            <div className="mt-3">
              <Field label="Custom Instructions (optional)">
                <textarea className={inputCls} rows={2} value={custom} onChange={(e)=>setCustom(e.target.value)} placeholder="Focus on implementation and real-world applications." />
              </Field>
            </div>
            <div className="mt-5 flex justify-end gap-3">
              <button onClick={()=>setShowReject(false)} className="rounded-md px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100">Cancel</button>
              <button onClick={reject} disabled={busy} className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50">
                {busy ? "Regenerating..." : "Submit and Regenerate"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── PAGE 3: Final syllabus ───────────────────────────────────────────────────

function FinalPage({ formData, result, onRestart }) {
  const [downloading, setDownloading] = useState(false);
  const coIds = result.cos.map((c) => c.co_id);
  const poIds = result.pos.map((p) => p.po_id);

  const downloadDocx = async () => {
    setDownloading(true);
    try {
      const r = await axios.post(`${G1}/export/docx`, {
        course_name:        formData.course_name,
        course_description: formData.course_description,
        course_code:        formData.course_code || null,
        num_units:          formData.num_units,
        education_level:    formData.education_level,
        programme:          formData.programme,
        year_of_study:      formData.year_of_study,
        semester:           formData.semester,
        branch:             formData.branch,
        credits:            formData.credits,
        ltp:                formData.ltp,
        university_name:    formData.university_name,
      }, { responseType: "blob", timeout: 1200000 });
      const url = URL.createObjectURL(r.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${formData.course_name.replaceAll(" ", "_")}_syllabus.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("DOCX export failed: " + (e.response?.data?.detail || e.message));
    } finally { setDownloading(false); }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 pb-16">
      <div className="rounded-xl bg-green-50 p-6 text-center ring-1 ring-green-200">
        <h2 className="text-2xl font-bold text-green-800">Syllabus Generated Successfully</h2>
        <p className="mt-1 text-green-700">{result.course_name} [{result.course_code}]</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {[["Total Units", result.units.length], ["Total COs", result.cos.length], ["Total POs", result.pos.length], ["Credits", formData.credits], ["Attainment Target", `${formData.attainment_settings?.target_score_percent ?? 60}%`]].map(([l, v]) => (
          <div key={l} className="rounded-lg bg-white p-4 text-center shadow-sm ring-1 ring-gray-200">
            <p className="text-2xl font-bold text-blue-900">{v}</p>
            <p className="mt-1 text-xs text-gray-500">{l}</p>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        {result.units.map((u, i) => (
          <div key={u.unit_id || i} className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-blue-900">{u.unit_id}: {u.unit_title}</h3>
              <span className="rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">{u.hours || 8} hrs</span>
            </div>
            {u.topics?.length > 0 && (
              <p className="mt-2 text-sm text-gray-700"><span className="font-medium">Topics:</span> {u.topics.join(", ")}</p>
            )}
            {u.unit_outcomes?.length > 0 && (
              <ul className="mt-2 list-inside list-disc text-sm text-gray-600">
                {u.unit_outcomes.map((o, j) => <li key={j}>{o}</li>)}
              </ul>
            )}
            {u.satisfied_cos?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {u.satisfied_cos.map((c) => <span key={c} className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">{c}</span>)}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h3 className="mb-3 font-semibold text-blue-900">CO-PO Mapping Matrix</h3>
        <MatrixTable rowIds={coIds} colIds={poIds} matrix={result.co_po_matrix} rowLabel="CO" />
        <Legend />
      </div>

      <div className="flex justify-center gap-4">
        <button onClick={downloadDocx} disabled={downloading}
          className="rounded-lg bg-blue-600 px-8 py-3 font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-50">
          {downloading ? "Generating DOCX..." : "Download DOCX"}
        </button>
        <button onClick={onRestart}
          className="rounded-lg bg-gray-200 px-8 py-3 font-semibold text-gray-700 hover:bg-gray-300">
          Generate Another Course
        </button>
      </div>
    </div>
  );
}

// ─── Root app ─────────────────────────────────────────────────────────────────

export default function App() {
  const [page, setPage] = useState(1);
  const [formData, setFormData] = useState(null);
  const [result, setResult] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="mb-8 bg-blue-900 py-6 text-center text-white shadow">
        <h1 className="text-2xl font-bold">AI Syllabus Generator</h1>
        <p className="mt-1 text-sm text-blue-200">NBA Compliant Curriculum Design</p>
        <div className="mt-3 flex justify-center gap-2 text-xs">
          {["Faculty Input", "Review", "Final Syllabus"].map((s, i) => (
            <span key={s} className={`rounded-full px-3 py-1 ${page === i + 1 ? "bg-white text-blue-900 font-semibold" : "bg-blue-800 text-blue-300"}`}>
              {i + 1}. {s}
            </span>
          ))}
        </div>
      </header>

      <main className="px-4">
        {page === 1 && (
          <FormPage onGenerated={(form, res) => { setFormData(form); setResult(res); setPage(2); }} />
        )}
        {page === 2 && result && (
          <ReviewPage
            formData={formData}
            result={result}
            onApproved={(res) => { setResult(res); setPage(3); }}
            onRejectedResult={(res) => setResult(res)}
          />
        )}
        {page === 3 && result && (
          <FinalPage formData={formData} result={result}
            onRestart={() => { setFormData(null); setResult(null); setPage(1); }} />
        )}
      </main>
    </div>
  );
}
