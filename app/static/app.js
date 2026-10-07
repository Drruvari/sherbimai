const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function markdownLite(text) {
  let safe = escapeHtml(text);
  safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  const lines = safe.split("\n");
  let html = "";
  let inUl = false;
  let inOl = false;

  const closeLists = () => {
    if (inUl) { html += "</ul>"; inUl = false; }
    if (inOl) { html += "</ol>"; inOl = false; }
  };

  for (const line of lines) {
    if (/^- /.test(line)) {
      if (!inUl) { closeLists(); html += "<ul>"; inUl = true; }
      html += `<li>${line.slice(2)}</li>`;
    } else if (/^\d+\. /.test(line)) {
      if (!inOl) { closeLists(); html += "<ol>"; inOl = true; }
      html += `<li>${line.replace(/^\d+\. /, "")}</li>`;
    } else if (!line.trim()) {
      closeLists();
    } else {
      closeLists();
      html += `<p>${line}</p>`;
    }
  }
  closeLists();
  return html;
}

async function ask(question) {
  const q = question.trim();
  if (q.length < 2) return;

  $("ask").disabled = true;
  $("status").textContent = "Po kërkoj në shërbimet e verifikuara…";
  $("result").classList.add("hidden");

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q })
    });

    if (!response.ok) throw new Error("Kërkesa dështoi.");
    const data = await response.json();

    if (!data.matched) {
      $("status").textContent = data.answer;
      return;
    }

    $("status").textContent = "";
    $("service-title").textContent = data.service.title;
    $("confidence").textContent = `${Math.round(data.confidence * 100)}% përputhje`;
    $("answer").innerHTML = markdownLite(data.answer);
    $("source").href = data.service.source_url;
    $("verified").textContent = `Kontrolluar më ${data.service.verified_at}`;

    const alts = data.alternatives || [];
    $("alternatives-wrap").style.display = alts.length ? "block" : "none";
    $("alternatives").innerHTML = alts
      .map(a => `<div class="alt"><strong>${escapeHtml(a.title)}</strong><br><span>${Math.round(a.score * 100)}% përputhje</span></div>`)
      .join("");

    $("result").classList.remove("hidden");
  } catch (err) {
    $("status").textContent = "Gabim gjatë kërkesës. Provo përsëri.";
  } finally {
    $("ask").disabled = false;
  }
}

$("ask").addEventListener("click", () => ask($("question").value));
$("question").addEventListener("keydown", (e) => {
  if (e.key === "Enter") ask(e.target.value);
});

document.querySelectorAll("[data-q]").forEach((button) => {
  button.addEventListener("click", () => {
    $("question").value = button.dataset.q;
    ask(button.dataset.q);
  });
});
