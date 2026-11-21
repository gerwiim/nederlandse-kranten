// GEGENEREERD uit app.jsx — wijzig app.jsx, dit bestand wordt automatisch opnieuw gebouwd.
const { useState, useEffect } = React;
const now = /* @__PURE__ */ new Date();
const vandaag = [
  now.getFullYear(),
  String(now.getMonth() + 1).padStart(2, "0"),
  String(now.getDate()).padStart(2, "0")
].join("-");
const krantenMeta = [
  { naam: "Algemeen Dagblad", url: "https://www.ad.nl/", kleur: "#E2001A" },
  { naam: "Nederlands Dagblad", url: "https://www.nd.nl/", kleur: "#005B8E" },
  { naam: "NRC", url: "https://www.nrc.nl/", kleur: "#003082" },
  { naam: "Het Parool", url: "https://www.parool.nl/", kleur: "#1A1A1A" },
  { naam: "Reformatorisch Dagblad", url: "https://www.rd.nl/", kleur: "#2E5E2E" },
  { naam: "De Telegraaf", url: "https://www.telegraaf.nl/", kleur: "#E30613" },
  { naam: "Trouw", url: "https://www.trouw.nl/", kleur: "#E87722" },
  { naam: "de Volkskrant", url: "https://www.volkskrant.nl/", kleur: "#CC0000" }
];
function hogeResolutieUrl(naam, datum) {
  if (naam !== "Reformatorisch Dagblad" || !datum) return null;
  const [j, m, d] = datum.split("-");
  return `https://www.digibron.nl/images/generated/reformatorisch-dagblad/katern-nieuws/${j}/${m}/${d}/1-large.jpg`;
}
function KrantAfbeelding({ src, alt, stijl, foutStijl }) {
  const [fout, setFout] = useState(false);
  useEffect(() => {
    setFout(false);
  }, [src]);
  if (fout || !src) {
    const extern = src && src.startsWith("http");
    return /* @__PURE__ */ React.createElement("div", { style: foutStijl }, extern ? /* @__PURE__ */ React.createElement(
      "a",
      {
        href: src,
        target: "_blank",
        rel: "noopener noreferrer",
        onClick: (e) => e.stopPropagation(),
        style: { color: "#555", fontWeight: "bold" }
      },
      "\u{1F4F0} Bekijk voorpagina \u2197"
    ) : /* @__PURE__ */ React.createElement(React.Fragment, null, "\u26A0\uFE0F Voorpagina", /* @__PURE__ */ React.createElement("br", null), "niet beschikbaar"));
  }
  return /* @__PURE__ */ React.createElement("img", { src, alt, style: stijl, onError: () => setFout(true) });
}
function formatDatum(dateStr) {
  const d = /* @__PURE__ */ new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("nl-NL", { weekday: "long", day: "numeric", month: "long" });
}
function App() {
  const [index, setIndex] = useState(null);
  const [geselecteerdeDatum, setGeselecteerdeDatum] = useState(null);
  const [archief, setArchief] = useState(null);
  const [archiefFout, setArchiefFout] = useState(false);
  const [bijgewerkt, setBijgewerkt] = useState(null);
  useEffect(() => {
    fetch(`archive.json?t=${Date.now()}`).then((r) => r.json()).then((data) => {
      setArchief(data);
      const datums = Object.keys(data).sort().reverse();
      if (datums.length) setGeselecteerdeDatum(datums[0]);
    }).catch(() => setArchiefFout(true));
    fetch(`status.json?t=${Date.now()}`).then((r) => r.json()).then((data) => setBijgewerkt(data.bijgewerkt || null)).catch(() => {
    });
  }, []);
  const beschikbareDatums = archief ? Object.keys(archief).sort().reverse() : [];
  const dagData = archief && geselecteerdeDatum && archief[geselecteerdeDatum] || {};
  const kranten = archief && geselecteerdeDatum ? krantenMeta.map((k) => ({ ...k, voorpagina: dagData[k.naam] || null })) : [];
  const geselecteerd = index !== null ? kranten[index] : null;
  const vorigeKrant = () => setIndex((index - 1 + kranten.length) % kranten.length);
  const volgendeKrant = () => setIndex((index + 1) % kranten.length);
  useEffect(() => {
    if (index === null) return;
    const handler = (e) => {
      if (e.key === "ArrowLeft") vorigeKrant();
      if (e.key === "ArrowRight") volgendeKrant();
      if (e.key === "Escape") setIndex(null);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [index, kranten]);
  const kopDatum = geselecteerdeDatum ? (/* @__PURE__ */ new Date(geselecteerdeDatum + "T12:00:00")).toLocaleDateString("nl-NL", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric"
  }) : "";
  let bijgewerktTekst = null;
  if (bijgewerkt) {
    const t = new Date(bijgewerkt);
    const tijd = t.toLocaleTimeString("nl-NL", { hour: "2-digit", minute: "2-digit" });
    bijgewerktTekst = bijgewerkt.slice(0, 10) === vandaag ? `Bijgewerkt om ${tijd}` : `Bijgewerkt op ${t.toLocaleDateString("nl-NL", { weekday: "long", day: "numeric", month: "long" })} om ${tijd}`;
  }
  const nieuwsteDatum = beschikbareDatums[0];
  let melding = null;
  if (nieuwsteDatum && geselecteerdeDatum === nieuwsteDatum && nieuwsteDatum !== vandaag) {
    melding = now.getDay() === 0 ? "Op zondag verschijnen er geen kranten. Hieronder de voorpagina's van zaterdag." : "De voorpagina's van vandaag zijn nog niet binnen. Hieronder de meest recente.";
  }
  const pijlStijl = {
    background: "rgba(255,255,255,0.15)",
    border: "none",
    color: "white",
    fontSize: "1.8rem",
    cursor: "pointer",
    borderRadius: "50%",
    width: "48px",
    height: "48px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    transition: "background 0.15s"
  };
  return /* @__PURE__ */ React.createElement("div", { style: { fontFamily: "Georgia, serif", background: "#f4f1ec", minHeight: "100vh", paddingBottom: "48px" } }, /* @__PURE__ */ React.createElement("div", { style: { background: "#1a1a1a", color: "white", padding: "24px 32px", marginBottom: "24px" } }, /* @__PURE__ */ React.createElement("h1", { style: { margin: 0, fontSize: "2rem", letterSpacing: "1px" } }, "\u{1F4F0} Nederlandse Kranten"), /* @__PURE__ */ React.createElement("p", { style: { margin: "6px 0 0 0", color: "#aaa", fontSize: "0.95rem" } }, geselecteerdeDatum === vandaag ? "Voorpagina's van vandaag" : "Voorpagina's", kopDatum && ` \u2014 ${kopDatum}`), bijgewerktTekst && /* @__PURE__ */ React.createElement("p", { style: { margin: "4px 0 0 0", color: "#777", fontSize: "0.8rem" } }, bijgewerktTekst)), melding && /* @__PURE__ */ React.createElement("div", { style: {
    margin: "0 32px 20px",
    padding: "10px 16px",
    background: "#fff8e1",
    border: "1px solid #f0d98c",
    borderRadius: "8px",
    color: "#6b5a1e",
    fontSize: "0.9rem"
  } }, melding), /* @__PURE__ */ React.createElement("div", { style: { padding: "0 32px", marginBottom: "28px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" } }, /* @__PURE__ */ React.createElement("span", { style: { fontWeight: "bold", fontSize: "0.95rem", color: "#444" } }, "Datum:"), /* @__PURE__ */ React.createElement(
    "select",
    {
      value: geselecteerdeDatum || "",
      onChange: (e) => {
        setGeselecteerdeDatum(e.target.value);
        setIndex(null);
      },
      style: {
        padding: "8px 14px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        fontSize: "0.95rem",
        background: "white",
        cursor: "pointer",
        fontFamily: "Georgia, serif"
      }
    },
    beschikbareDatums.map((d) => /* @__PURE__ */ React.createElement("option", { key: d, value: d }, d === vandaag ? `Vandaag \u2014 ${formatDatum(d)}` : formatDatum(d)))
  ), archiefFout && /* @__PURE__ */ React.createElement("span", { style: { color: "#c00", fontSize: "0.85rem" } }, "\u26A0\uFE0F Archief kon niet worden geladen")), kranten.length === 0 ? /* @__PURE__ */ React.createElement("div", { style: { padding: "0 32px", color: "#888" } }, archief || archiefFout ? "Geen voorpagina's beschikbaar voor deze datum." : "Laden\u2026") : /* @__PURE__ */ React.createElement("div", { style: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "24px",
    padding: "0 32px"
  } }, kranten.map((krant, i) => /* @__PURE__ */ React.createElement(
    "div",
    {
      key: krant.naam,
      onClick: () => setIndex(i),
      style: {
        background: "white",
        borderRadius: "10px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.10)",
        overflow: "hidden",
        cursor: "pointer",
        transition: "transform 0.15s, box-shadow 0.15s"
      },
      onMouseEnter: (e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.18)";
      },
      onMouseLeave: (e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "0 2px 12px rgba(0,0,0,0.10)";
      }
    },
    /* @__PURE__ */ React.createElement("div", { style: { background: krant.kleur, padding: "10px 16px" } }, /* @__PURE__ */ React.createElement("span", { style: { color: "white", fontWeight: "bold", fontSize: "1rem" } }, krant.naam)),
    /* @__PURE__ */ React.createElement("div", { style: {
      background: "#e8e4dc",
      height: "340px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      overflow: "hidden"
    } }, /* @__PURE__ */ React.createElement(
      KrantAfbeelding,
      {
        src: krant.voorpagina,
        alt: `Voorpagina ${krant.naam}`,
        stijl: { width: "100%", height: "100%", objectFit: "cover" },
        foutStijl: { color: "#999", textAlign: "center", padding: "20px", fontSize: "0.9rem" }
      }
    )),
    /* @__PURE__ */ React.createElement("div", { style: { padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" } }, /* @__PURE__ */ React.createElement("span", { style: { fontSize: "0.8rem", color: "#888" } }, "Klik voor volledig scherm"), /* @__PURE__ */ React.createElement(
      "a",
      {
        href: krant.url,
        target: "_blank",
        rel: "noopener noreferrer",
        onClick: (e) => e.stopPropagation(),
        style: { fontSize: "0.8rem", color: krant.kleur, textDecoration: "none", fontWeight: "bold" }
      },
      "Naar website \u2192"
    ))
  ))), geselecteerd && /* @__PURE__ */ React.createElement(
    "div",
    {
      onClick: () => setIndex(null),
      style: {
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.88)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1e3,
        padding: "20px",
        gap: "16px"
      }
    },
    /* @__PURE__ */ React.createElement(
      "button",
      {
        onClick: (e) => {
          e.stopPropagation();
          vorigeKrant();
        },
        style: pijlStijl,
        onMouseEnter: (e) => e.currentTarget.style.background = "rgba(255,255,255,0.30)",
        onMouseLeave: (e) => e.currentTarget.style.background = "rgba(255,255,255,0.15)"
      },
      "\u2039"
    ),
    /* @__PURE__ */ React.createElement(
      "div",
      {
        onClick: (e) => e.stopPropagation(),
        style: {
          background: "white",
          borderRadius: "12px",
          overflow: "hidden",
          maxWidth: "560px",
          width: "100%",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column"
        }
      },
      /* @__PURE__ */ React.createElement("div", { style: {
        background: geselecteerd.kleur,
        padding: "14px 20px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexShrink: 0
      } }, /* @__PURE__ */ React.createElement("span", { style: { color: "white", fontWeight: "bold", fontSize: "1.1rem" } }, index + 1, "/", kranten.length, " \u2014 ", geselecteerd.naam), /* @__PURE__ */ React.createElement(
        "button",
        {
          onClick: () => setIndex(null),
          style: { background: "none", border: "none", color: "white", fontSize: "1.4rem", cursor: "pointer", lineHeight: 1 }
        },
        "\u2715"
      )),
      /* @__PURE__ */ React.createElement("div", { style: { overflowY: "auto", flexGrow: 1 } }, /* @__PURE__ */ React.createElement(
        KrantAfbeelding,
        {
          src: geselecteerd.voorpagina,
          alt: `Voorpagina ${geselecteerd.naam}`,
          stijl: { width: "100%", display: "block" },
          foutStijl: { padding: "40px", textAlign: "center", color: "#999" }
        }
      )),
      /* @__PURE__ */ React.createElement("div", { style: {
        padding: "14px 20px",
        borderTop: "1px solid #eee",
        flexShrink: 0,
        display: "flex",
        justifyContent: "flex-end",
        gap: "20px",
        flexWrap: "wrap"
      } }, hogeResolutieUrl(geselecteerd.naam, geselecteerdeDatum) && /* @__PURE__ */ React.createElement(
        "a",
        {
          href: hogeResolutieUrl(geselecteerd.naam, geselecteerdeDatum),
          target: "_blank",
          rel: "noopener noreferrer",
          style: { color: geselecteerd.kleur, fontWeight: "bold", textDecoration: "none" }
        },
        "Bekijk in hoge resolutie \u2197"
      ), /* @__PURE__ */ React.createElement(
        "a",
        {
          href: geselecteerd.url,
          target: "_blank",
          rel: "noopener noreferrer",
          style: { color: geselecteerd.kleur, fontWeight: "bold", textDecoration: "none" }
        },
        "Bezoek ",
        geselecteerd.naam,
        " \u2192"
      ))
    ),
    /* @__PURE__ */ React.createElement(
      "button",
      {
        onClick: (e) => {
          e.stopPropagation();
          volgendeKrant();
        },
        style: pijlStijl,
        onMouseEnter: (e) => e.currentTarget.style.background = "rgba(255,255,255,0.30)",
        onMouseLeave: (e) => e.currentTarget.style.background = "rgba(255,255,255,0.15)"
      },
      "\u203A"
    )
  ));
}
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(/* @__PURE__ */ React.createElement(App, null));
