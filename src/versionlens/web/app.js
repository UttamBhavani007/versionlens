"use strict";

(() => {
  const byId = (id) => document.getElementById(id);
  const ui = {
    form: byId("question-form"), question: byId("question"), version: byId("version"),
    retriever: byId("retriever"), search: byId("search-button"), ask: byId("ask-button"),
    error: byId("question-error"), count: byId("character-count"), status: byId("request-status"),
    result: byId("result-body"), title: byId("results-title"), context: byId("result-context"),
    resultsPanel: document.querySelector(".results"), corpus: byId("corpus-count"),
    catalogError: byId("catalog-error"), catalogMessage: byId("catalog-error-message"),
    retry: byId("retry-catalog"), dialog: byId("source-dialog"), sourceTitle: byId("source-title"),
    sourceBody: byId("source-body"), closeSource: byId("close-source"),
  };
  const METHODS = { keyword: "Keyword", vector: "Vector · experimental", hybrid: "Hybrid · experimental" };
  const VERSIONS = new Set(["0.27.2", "0.28.1"]);
  const EXAMPLES = {
    timeout: "What is the default timeout in HTTPX?",
    upgrade: "Why did the proxies argument stop working after upgrading?",
    missing: "quantumgiraffeunsupported",
  };
  const REASONS = {
    no_matching_evidence: "No matching evidence was found for this HTTPX version.",
    no_lexical_support_for_experimental_retrieval: "No keyword support was found. The experimental retriever and local model did not run.",
    no_usable_quote_spans: "The matching excerpts did not contain a quotation this draft pipeline can use.",
    context_budget_exceeded: "The available evidence did not fit the local model’s context budget.",
    insufficient_evidence: "The supplied excerpts were insufficient for a draft.",
    conflicting_evidence: "The model reported unresolved conflicting evidence.",
    unrelated_evidence: "The model judged the retrieved excerpts unrelated to the question.",
    invalid_generation: "The model draft failed validation and was withheld.",
    local_model_error: "The local model is unavailable or returned an unusable response. Check the local runtime and try again.",
  };
  const state = { catalog: null, busy: false, epoch: 0, controller: null, inspector: null, currentResult: null };

  function node(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined) item.textContent = text;
    return item;
  }

  function status(message, kind = "") {
    ui.status.textContent = message;
    ui.status.className = "request-status" + (kind ? ` is-${kind}` : "");
  }

  function updateButtons() {
    ui.search.disabled = !state.catalog || state.busy;
    ui.ask.disabled = !state.catalog || state.busy;
    ui.resultsPanel.setAttribute("aria-busy", String(state.busy));
  }

  function clearQuestionError() {
    ui.question.removeAttribute("aria-invalid");
    ui.error.textContent = "";
    ui.error.hidden = true;
  }

  function questionError(message) {
    ui.error.textContent = message;
    ui.error.hidden = false;
    ui.question.setAttribute("aria-invalid", "true");
    ui.question.focus();
    status(message, "error");
  }

  function emptyState() {
    const empty = node("div", "empty-state");
    const illustration = node("div", "source-illustration");
    illustration.setAttribute("aria-hidden", "true");
    illustration.append(node("span", "illustration-tag", "HTTPX"), node("i"), node("i"), node("i"), node("span", "illustration-corner", "↗"));
    empty.append(illustration, node("h3", "", "A version. A question. A source."),
      node("p", "", "Find documentation excerpts with exact source links. Then explore a cited draft if the evidence allows it."));
    ui.result.replaceChildren(empty);
    ui.title.textContent = "Inspect the evidence";
    ui.context.hidden = true;
  }

  function closeInspector() {
    if (state.inspector) state.inspector.abort();
    state.inspector = null;
    if (ui.dialog.open) ui.dialog.close();
  }

  function invalidate() {
    state.epoch += 1;
    if (state.controller) state.controller.abort();
    state.controller = null;
    state.currentResult = null;
    state.busy = false;
    closeInspector();
    clearQuestionError();
    ui.count.textContent = `${ui.question.value.length} / 2000`;
    emptyState();
    status(state.catalog ? "Inputs changed. Run a new search or draft for this selection." : "Connecting to your local workspace…");
    updateButtons();
  }

  function snapshot() {
    return { question: ui.question.value.trim(), version: ui.version.value, retriever: ui.retriever.value };
  }

  function isCurrent(selection, ticket) {
    const current = snapshot();
    return state.epoch === ticket && current.question === selection.question &&
      current.version === selection.version && current.retriever === selection.retriever;
  }

  async function jsonResponse(response) {
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error("The local service returned an unexpected response. Please try again.");
    }
    if (!response.ok) {
      const message = body && body.error && body.error.message;
      const error = new Error(typeof message === "string" && message.length <= 500 ? message : "The local request could not be completed.");
      error.httpStatus = response.status;
      throw error;
    }
    if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("The local service returned an invalid response.");
    return body;
  }

  function sourcePath(hit) {
    return hit.source_id.slice(`httpx:${hit.version}:`.length);
  }

  function citationUrl(hit) {
    if (typeof hit.citation_url !== "string" || hit.citation_url.length > 2048) return null;
    try {
      const url = new URL(hit.citation_url);
      if (url.href !== hit.citation_url || url.protocol !== "https:" || url.hostname !== "github.com" ||
          url.port || url.username || url.password || url.search !== "?plain=1") return null;
      const path = /^\/encode\/httpx\/blob\/([0-9a-f]{40})\/([A-Za-z0-9_.\/-]+\.md)$/.exec(url.pathname);
      const lines = /^#L([1-9]\d*)-L([1-9]\d*)$/.exec(url.hash);
      if (!path || !lines || path[2].split("/").some((part) => !part || part === "." || part === "..")) return null;
      if (path[1] !== hit.upstream_commit || Number(lines[1]) !== hit.start_line || Number(lines[2]) !== hit.end_line ||
          hit.source_id !== `httpx:${hit.version}:${path[2]}`) return null;
      return url.href;
    } catch {
      return null;
    }
  }

  function checkedHit(hit, version) {
    if (!hit || typeof hit !== "object" || hit.version !== version ||
        !/^[0-9a-f]{24}$/.test(hit.chunk_id) || !/^[0-9a-f]{64}$/.test(hit.source_sha256) ||
        !/^[0-9a-f]{40}$/.test(hit.upstream_commit) || typeof hit.source_id !== "string" ||
        !hit.source_id.startsWith(`httpx:${version}:`) || typeof hit.section !== "string" ||
        !hit.section.trim() || hit.section.length > 5000 || typeof hit.text !== "string" || hit.text.length > 2000000 ||
        !Number.isSafeInteger(hit.start_line) || !Number.isSafeInteger(hit.end_line) ||
        hit.start_line < 1 || hit.end_line < hit.start_line || !citationUrl(hit)) {
      throw new Error("The service returned inconsistent source metadata. Run a new search.");
    }
    return hit;
  }

  function sourceLink(hit, label = "Open source ↗", className = "source-link") {
    const link = node("a", className, label);
    link.href = citationUrl(hit);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", `${label.replace("↗", "").trim()}: ${sourcePath(hit)}, HTTPX ${hit.version}, lines ${hit.start_line} to ${hit.end_line} (opens in a new tab)`);
    return link;
  }

  function provenance(hit) {
    const list = node("dl", "provenance");
    const fields = [
      ["Version", `HTTPX ${hit.version}`], ["Source", sourcePath(hit)],
      ["Lines", `${hit.start_line}–${hit.end_line}`], ["Commit", hit.upstream_commit],
      ["SHA-256", hit.source_sha256], ["Chunk ID", hit.chunk_id],
    ];
    for (const [label, value] of fields) {
      const detail = node("dd", label === "Commit" || label === "SHA-256" || label === "Chunk ID" ? "mono" : "", value);
      list.append(node("dt", "", label), detail);
    }
    return list;
  }

  function evidenceCard(hit, rank, selection, ticket) {
    const card = node("article", "evidence-card");
    const top = node("div", "evidence-topline");
    const label = node("div", "evidence-label");
    label.append(node("span", "rank-number", String(rank).padStart(2, "0")), node("span", "version-badge", `HTTPX ${hit.version}`));
    top.append(label, sourceLink(hit));
    const details = node("details", "evidence-details");
    const inspect = node("button", "text-button", "Inspect source chunk →");
    inspect.type = "button";
    inspect.addEventListener("click", () => inspectSource(hit, selection, ticket));
    details.append(node("summary", "", "Read excerpt & provenance"), node("pre", "source-text", hit.text), provenance(hit), inspect);
    card.append(top, node("h3", "", hit.section), node("p", "source-lines", `${sourcePath(hit)} · lines ${hit.start_line}–${hit.end_line}`),
      node("p", "excerpt-preview", hit.text), details);
    return card;
  }

  function renderState(title, description, error = false, footnote = "") {
    const box = node("div", "result-state" + (error ? " is-error" : ""));
    box.append(node("h3", "", title), node("p", "", description));
    if (footnote) box.append(node("p", "state-footnote", footnote));
    ui.result.replaceChildren(box);
  }

  function setContext(selection) {
    ui.context.textContent = `HTTPX ${selection.version}`;
    ui.context.hidden = false;
  }

  function renderSearch(data, selection, ticket) {
    if (!Array.isArray(data.hits) || data.hits.length > 20) throw new Error("The local service returned an invalid evidence list.");
    const hits = data.hits.map((hit) => checkedHit(hit, selection.version));
    ui.title.textContent = hits.length ? "Evidence, with context" : "No matching evidence";
    setContext(selection);
    if (!hits.length) {
      renderState("No matching excerpts", "Try another focused question, or check that the selected snapshot contains the change you need.", false,
        "An empty keyword search does not prove the topic is absent from every document.");
      status("No matching evidence was returned. No answer was generated.");
      return;
    }
    const note = node("p", "result-note", `${hits.length} ranked excerpt${hits.length === 1 ? "" : "s"} · ${METHODS[selection.retriever]}. Ranking scores are not confidence.`);
    const list = node("div", "evidence-list");
    hits.forEach((hit, index) => list.append(evidenceCard(hit, index + 1, selection, ticket)));
    ui.result.replaceChildren(note, list);
    status("Source excerpts are ready. Check the section and release history before drawing a conclusion.");
  }

  function checkedClaims(data, version) {
    if (!Array.isArray(data.claims) || !data.claims.length || data.claims.length > 4) throw new Error("The local service returned an invalid draft.");
    return data.claims.map((claim) => {
      if (!claim || typeof claim.text !== "string" || !claim.text.trim() || claim.text.length > 4000 ||
          !Array.isArray(claim.citations) || !claim.citations.length || claim.citations.length > 3) {
        throw new Error("The local service returned an uncited draft. No draft is displayed.");
      }
      claim.citations.forEach((citation) => {
        checkedHit(citation, version);
        if (!/^E[1-4]$/.test(citation.evidence_id) || typeof citation.quote !== "string" ||
            !citation.quote || citation.quote.length > 600 || !citation.text.includes(citation.quote)) {
          throw new Error("The draft contains inconsistent citation metadata. No draft is displayed.");
        }
      });
      return claim;
    });
  }

  function renderDraft(data, selection, ticket) {
    setContext(selection);
    if (data.status === "error") {
      ui.title.textContent = "The draft could not be created";
      renderState("Local model unavailable", REASONS[data.reason] || "The local service could not complete this draft. Try finding evidence first.", true);
      status("The local request failed. No draft is displayed.", "error");
      return;
    }
    if (data.status === "abstained") {
      ui.title.textContent = "No draft was shown";
      renderState("Evidence before a guess", REASONS[data.reason] || "The service declined to produce a draft from the supplied evidence.", false,
        data.model_called === false ? "The generation model was not called." : "No partial model answer is displayed.");
      status("The service abstained. You can still use Find evidence to inspect the documentation.");
      return;
    }
    if (data.status !== "answered" || data.semantic_support_verified !== false) throw new Error("The local service returned an unexpected draft status.");
    const claims = checkedClaims(data, selection.version);
    const fragment = document.createDocumentFragment();
    fragment.append(node("p", "draft-notice", "Draft answer; check the cited sources. A real quote does not prove that the claim or release interpretation is correct."));
    const unique = new Map();
    for (const claim of claims) {
      const article = node("article", "draft-claim");
      article.append(node("p", "", claim.text));
      const links = node("div", "claim-citations");
      for (const citation of claim.citations) {
        links.append(sourceLink(citation, `${citation.evidence_id} · HTTPX ${citation.version}`, ""));
        article.append(node("blockquote", "citation-quote", citation.quote));
        if (!unique.has(citation.chunk_id)) unique.set(citation.chunk_id, citation);
      }
      article.append(links);
      fragment.append(article);
    }
    fragment.append(node("p", "draft-evidence-title", "INSPECT THE CITED EXCERPTS"));
    const evidence = node("div", "evidence-list");
    [...unique.values()].forEach((hit, index) => evidence.append(evidenceCard(hit, index + 1, selection, ticket)));
    fragment.append(evidence);
    ui.result.replaceChildren(fragment);
    ui.title.textContent = "A cited draft";
    status("Draft ready. Source identity and quotations were checked; semantic support remains unverified.");
  }

  function loadingState(action, selection) {
    ui.title.textContent = action === "search" ? "Finding source excerpts" : "Preparing a local draft";
    setContext(selection);
    const fragment = document.createDocumentFragment();
    for (let count = 0; count < 3; count += 1) {
      const skeleton = node("div", "skeleton");
      skeleton.setAttribute("aria-hidden", "true");
      skeleton.append(node("span"), node("span"), node("span"));
      fragment.append(skeleton);
    }
    ui.result.replaceChildren(fragment);
    status(action === "search" ? `Finding evidence for HTTPX ${selection.version}…` : `Retrieving evidence and checking a local draft for HTTPX ${selection.version}…`, "busy");
  }

  async function run(action) {
    if (!state.catalog || state.busy) return;
    const selection = snapshot();
    clearQuestionError();
    if (!selection.question) return questionError("Enter a question before continuing.");
    if (selection.question.length > 2000) return questionError("Keep your question within 2000 characters.");
    if (!state.catalog.versions.includes(selection.version) || !state.catalog.retrievers.includes(selection.retriever)) {
      status("Choose a supported version and retrieval method.", "error");
      return;
    }
    const ticket = ++state.epoch;
    closeInspector();
    state.currentResult = null;
    const controller = new AbortController();
    state.controller = controller;
    state.busy = true;
    updateButtons();
    loadingState(action, selection);
    let timedOut = false;
    const timeout = window.setTimeout(() => { timedOut = true; controller.abort(); }, 150000);
    try {
      const response = await fetch(`/api/${action}`, {
        method: "POST", credentials: "same-origin", cache: "no-store", signal: controller.signal,
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ ...selection, limit: 5 }),
      });
      const data = await jsonResponse(response);
      if (!isCurrent(selection, ticket)) return;
      if (data.version !== selection.version || data.question !== selection.question || data.retrieval_method !== selection.retriever) {
        throw new Error("The response does not match your current question, version and retrieval method. Run a new request.");
      }
      if (action === "search") renderSearch(data, selection, ticket);
      else renderDraft(data, selection, ticket);
      state.currentResult = selection;
    } catch (error) {
      if (!isCurrent(selection, ticket) || (controller.signal.aborted && !timedOut)) return;
      const message = timedOut ? "The local request took too long. Try finding evidence first." :
        error instanceof TypeError ? "Could not reach the local service. Check that the workspace is still running." : error.message;
      ui.title.textContent = "Request could not be completed";
      renderState("Something needs attention", message, true, "Your question and selection have been kept.");
      if (error.httpStatus === 400) questionError(message);
      else status(message, "error");
    } finally {
      window.clearTimeout(timeout);
      if (state.epoch === ticket) {
        state.busy = false;
        state.controller = null;
        updateButtons();
      }
    }
  }

  async function inspectSource(hit, selection, ticket) {
    if (!isCurrent(selection, ticket) || state.currentResult !== selection) return;
    if (state.inspector) state.inspector.abort();
    const controller = new AbortController();
    state.inspector = controller;
    ui.sourceTitle.textContent = "Source chunk";
    ui.sourceBody.replaceChildren(node("p", "field-help", "Loading the original source chunk…"));
    if (!ui.dialog.open) ui.dialog.showModal();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
      const url = new URL(`/api/chunks/${encodeURIComponent(hit.chunk_id)}`, window.location.origin);
      url.searchParams.set("version", selection.version);
      const response = await fetch(url.pathname + url.search, { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" }, signal: controller.signal });
      const chunk = checkedHit(await jsonResponse(response), selection.version);
      if (!isCurrent(selection, ticket) || !ui.dialog.open || state.inspector !== controller) return;
      if (chunk.chunk_id !== hit.chunk_id || chunk.source_sha256 !== hit.source_sha256 || chunk.upstream_commit !== hit.upstream_commit || chunk.text !== hit.text) {
        throw new Error("The source changed after this result. Close the inspector and find evidence again.");
      }
      ui.sourceTitle.textContent = sourcePath(chunk);
      ui.sourceBody.replaceChildren(node("span", "version-badge", `HTTPX ${chunk.version}`),
        node("pre", "source-text", chunk.text), provenance(chunk), sourceLink(chunk, "Open original source ↗"));
    } catch (error) {
      if (!isCurrent(selection, ticket) || !ui.dialog.open || state.inspector !== controller) return;
      ui.sourceBody.replaceChildren(node("p", "field-error", controller.signal.aborted ? "The source request timed out. Close the inspector and try again." : error.message));
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function loadCatalog() {
    ui.retry.disabled = true;
    ui.catalogError.hidden = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch("/api/catalog", { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" }, signal: controller.signal });
      const catalog = await jsonResponse(response);
      if (catalog.product !== "httpx" || !Array.isArray(catalog.versions) || !catalog.versions.length ||
          !catalog.versions.every((version) => VERSIONS.has(version)) || !Array.isArray(catalog.retrievers) ||
          !catalog.retrievers.length || !catalog.retrievers.every((method) => Object.hasOwn(METHODS, method)) ||
          catalog.default_retriever !== "keyword" || !catalog.retrievers.includes("keyword")) {
        throw new Error("The local service returned an unsupported documentation catalog.");
      }
      state.catalog = catalog;
      ui.version.replaceChildren(...catalog.versions.map((version) => {
        const option = node("option", "", `HTTPX ${version}`);
        option.value = version;
        return option;
      }));
      ui.version.value = catalog.versions.includes("0.28.1") ? "0.28.1" : catalog.versions[0];
      ui.retriever.replaceChildren(...catalog.retrievers.map((method) => {
        const option = node("option", "", METHODS[method]);
        option.value = method;
        return option;
      }));
      ui.retriever.value = "keyword";
      ui.version.disabled = false;
      ui.retriever.disabled = false;
      const index = catalog.index;
      ui.corpus.textContent = index && Number.isSafeInteger(index.sources) && Number.isSafeInteger(index.chunks) && index.sources >= 0 && index.chunks >= 0 ?
        `${index.sources} source files · ${index.chunks} indexed excerpts` : "Local documentation is ready";
      invalidate();
      status("Ready. Find source excerpts first, or request a local draft.");
    } catch (error) {
      state.catalog = null;
      ui.catalogMessage.textContent = controller.signal.aborted ? "The local catalog did not respond. Check that the workspace is running." :
        error instanceof TypeError ? "Could not reach the local service. Check that the workspace is running." : error.message;
      ui.catalogError.hidden = false;
      ui.corpus.textContent = "Local documentation unavailable";
      status("Could not load the local workspace. Try connecting again.", "error");
      updateButtons();
    } finally {
      window.clearTimeout(timeout);
      ui.retry.disabled = false;
    }
  }

  ui.form.addEventListener("submit", (event) => { event.preventDefault(); run("search"); });
  ui.ask.addEventListener("click", () => run("ask"));
  ui.question.addEventListener("input", invalidate);
  ui.version.addEventListener("change", invalidate);
  ui.retriever.addEventListener("change", invalidate);
  ui.retry.addEventListener("click", loadCatalog);
  ui.closeSource.addEventListener("click", closeInspector);
  ui.dialog.addEventListener("close", () => { if (state.inspector) state.inspector.abort(); state.inspector = null; });
  for (const button of document.querySelectorAll("[data-example]")) {
    button.addEventListener("click", () => {
      ui.question.value = EXAMPLES[button.dataset.example];
      invalidate();
      ui.question.focus();
    });
  }
  ui.count.textContent = `${ui.question.value.length} / 2000`;
  loadCatalog();
})();
