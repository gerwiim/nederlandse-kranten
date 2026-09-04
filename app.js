const { useState, useEffect } = React;

const now = new Date();
const yyyy = now.getFullYear();
const mm = String(now.getMonth() + 1).padStart(2, "0");
const dd = String(now.getDate()).padStart(2, "0");
const vandaag = `${yyyy}-${mm}-${dd}`;

function getRdDatum() {
  const d = new Date();
  if (d.getDay() === 0) d.setDate(d.getDate() - 1);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dag = String(d.getDate()).padStart(2, "0");
  return `${y}${m}${dag}`;
}
const rdDatum = getRdDatum();

const krantenVandaag = [
  { naam: "Algemeen Dagblad",       url: "https://www.ad.nl/",         voorpagina: "https://cdn-03.tapp.dpgmedia.cloud/packshot/ad/ad/latest.png",                                    kleur: "#E2001A" },
  { naam: "Nederlands Dagblad",     url: "https://www.nd.nl/",         voorpagina: "https://storage.pubble.cloud/9ed0159c/paper/f9da25e6/files/large/1.jpg",                          kleur: "#005B8E" },
  { naam: "NRC",                    url: "https://www.nrc.nl/",        voorpagina: "https://s3-eu-west-1.amazonaws.com/nrchub/pages/NH/20260904/101-full-8a03fb.jpg",                 kleur: "#003082" },
  { naam: "Het Parool",             url: "https://www.parool.nl/",     voorpagina: "https://cdn-03.tapp.dpgmedia.cloud/packshot/hp/latest.png",                                       kleur: "#1A1A1A" },
  { naam: "Reformatorisch Dagblad", url: "https://www.rd.nl/",         voorpagina: `https://cdn.erdee.nl/epaper/_fpage/RDB/2026/RDB_RDB_20260904.jpg`,                           kleur: "#2E5E2E" },
  { naam: "De Telegraaf",           url: "https://www.telegraaf.nl/",  voorpagina: "https://mhu-tlg-webreader-production.twipemobile.com/data/3461/covers/Preview-MEDIUM-273558.jpg", kleur: "#E30613" },
  { naam: "Trouw",                  url: "https://www.trouw.nl/",      voorpagina: "https://cdn-03.tapp.dpgmedia.cloud/packshot/tr/latest.png",                                       kleur: "#E87722" },
  { naam: "de Volkskrant",          url: "https://www.volkskrant.nl/", voorpagina: "https://cdn-03.tapp.dpgmedia.cloud/packshot/vk/latest.png",                                       kleur: "#CC0000" },
];

const krantenMeta = Object.fromEntries(
  krantenVandaag.map(k => [k.naam, { url: k.url, kleur: k.kleur }])
);

function KrantAfbeelding({ src, alt, stijl, foutStijl }) {
  const [fout, setFout] = useState(false);
  useEffect(() => { setFout(false); }, [src]);
  if (fout) return <div style={foutStijl}>⚠️ Voorpagina<br />niet beschikbaar</div>;
  return <img src={src} alt={alt} style={stijl} onError={() => setFout(true)} />;
}

function formatDatum(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("nl-NL", { weekday: "long", day: "numeric", month: "long" });
}

function App() {
  const [index, setIndex] = useState(null);
  const [geselecteerdeDatum, setGeselecteerdeDatum] = useState(vandaag);
  const [archief, setArchief] = useState(null);
  const [archiefFout, setArchiefFout] = useState(false);

  useEffect(() => {
    fetch("archive.json")
      .then(r => r.json())
      .then(data => setArchief(data))
      .catch(() => setArchiefFout(true));
  }, []);

  const isVandaag = geselecteerdeDatum === vandaag;
  let kranten;
  if (isVandaag) {
    kranten = krantenVandaag;
  } else if (archief && archief[geselecteerdeDatum]) {
    kranten = Object.entries(archief[geselecteerdeDatum]).map(([naam, voorpagina]) => ({
      naam,
      voorpagina,
      url: krantenMeta[naam]?.url || "#",
      kleur: krantenMeta[naam]?.kleur || "#333",
    }));
  } else {
    kranten = [];
  }

  const beschikbareDatums = archief
    ? [vandaag, ...Object.keys(archief).filter(d => d !== vandaag).sort().reverse()]
    : [vandaag];

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

  const today = now.toLocaleDateString("nl-NL", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  const pijlStijl = {
    background: "rgba(255,255,255,0.15)", border: "none", color: "white",
    fontSize: "1.8rem", cursor: "pointer", borderRadius: "50%",
    width: "48px", height: "48px", display: "flex", alignItems: "center",
    justifyContent: "center", flexShrink: 0, transition: "background 0.15s",
  };

  return (
    <div style={{ fontFamily: "Georgia, serif", background: "#f4f1ec", minHeight: "100vh", paddingBottom: "48px" }}>

      {/* Header */}
      <div style={{ background: "#1a1a1a", color: "white", padding: "24px 32px", marginBottom: "24px" }}>
        <h1 style={{ margin: 0, fontSize: "2rem", letterSpacing: "1px" }}>📰 Nederlandse Kranten</h1>
        <p style={{ margin: "6px 0 0 0", color: "#aaa", fontSize: "0.95rem" }}>
          Voorpagina's van vandaag — {today}
        </p>
      </div>

      {/* Datumkiezer */}
      <div style={{ padding: "0 32px", marginBottom: "28px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
        <span style={{ fontWeight: "bold", fontSize: "0.95rem", color: "#444" }}>Datum:</span>
        <select
          value={geselecteerdeDatum}
          onChange={e => { setGeselecteerdeDatum(e.target.value); setIndex(null); }}
          style={{
            padding: "8px 14px", borderRadius: "8px", border: "1px solid #ccc",
            fontSize: "0.95rem", background: "white", cursor: "pointer",
            fontFamily: "Georgia, serif",
          }}
        >
          {beschikbareDatums.map(d => (
            <option key={d} value={d}>
              {d === vandaag ? `Vandaag — ${formatDatum(d)}` : formatDatum(d)}
            </option>
          ))}
        </select>
        {archiefFout && (
          <span style={{ color: "#c00", fontSize: "0.85rem" }}>⚠️ Archief kon niet worden geladen</span>
        )}
      </div>

      {/* Krantenraster */}
      {kranten.length === 0 ? (
        <div style={{ padding: "0 32px", color: "#888" }}>
          Geen voorpagina's beschikbaar voor deze datum.
        </div>
      ) : (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "24px",
          padding: "0 32px",
        }}>
          {kranten.map((krant, i) => (
            <div
              key={krant.naam}
              onClick={() => setIndex(i)}
              style={{
                background: "white", borderRadius: "10px",
                boxShadow: "0 2px 12px rgba(0,0,0,0.10)", overflow: "hidden",
                cursor: "pointer", transition: "transform 0.15s, box-shadow 0.15s",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.18)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 2px 12px rgba(0,0,0,0.10)";
              }}
            >
              <div style={{ background: krant.kleur, padding: "10px 16px" }}>
                <span style={{ color: "white", fontWeight: "bold", fontSize: "1rem" }}>{krant.naam}</span>
              </div>
              <div style={{
                background: "#e8e4dc", height: "340px",
                display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden",
              }}>
                <KrantAfbeelding
                  src={krant.voorpagina}
                  alt={`Voorpagina ${krant.naam}`}
                  stijl={{ width: "100%", height: "100%", objectFit: "cover" }}
                  foutStijl={{ color: "#999", textAlign: "center", padding: "20px", fontSize: "0.9rem" }}
                />
              </div>
              <div style={{ padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.8rem", color: "#888" }}>Klik voor volledig scherm</span>
                <a
                  href={krant.url} target="_blank" rel="noopener noreferrer"
                  onClick={e => e.stopPropagation()}
                  style={{ fontSize: "0.8rem", color: krant.kleur, textDecoration: "none", fontWeight: "bold" }}
                >
                  Naar website →
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {geselecteerd && (
        <div
          onClick={() => setIndex(null)}
          style={{
            position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
            background: "rgba(0,0,0,0.88)", display: "flex", alignItems: "center",
            justifyContent: "center", zIndex: 1000, padding: "20px", gap: "16px",
          }}
        >
          <button
            onClick={e => { e.stopPropagation(); vorigeKrant(); }}
            style={pijlStijl}
            onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.30)"}
            onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.15)"}
          >‹</button>

          <div
            onClick={e => e.stopPropagation()}
            style={{
              background: "white", borderRadius: "12px", overflow: "hidden",
              maxWidth: "560px", width: "100%", maxHeight: "90vh",
              display: "flex", flexDirection: "column",
            }}
          >
            <div style={{
              background: geselecteerd.kleur, padding: "14px 20px",
              display: "flex", justifyContent: "space-between", alignItems: "center", flexShrink: 0,
            }}>
              <span style={{ color: "white", fontWeight: "bold", fontSize: "1.1rem" }}>
                {index + 1}/{kranten.length} — {geselecteerd.naam}
              </span>
              <button
                onClick={() => setIndex(null)}
                style={{ background: "none", border: "none", color: "white", fontSize: "1.4rem", cursor: "pointer", lineHeight: 1 }}
              >✕</button>
            </div>
            <div style={{ overflowY: "auto", flexGrow: 1 }}>
              <KrantAfbeelding
                src={geselecteerd.voorpagina}
                alt={`Voorpagina ${geselecteerd.naam}`}
                stijl={{ width: "100%", display: "block" }}
                foutStijl={{ padding: "40px", textAlign: "center", color: "#999" }}
              />
            </div>
            <div style={{ padding: "14px 20px", textAlign: "right", borderTop: "1px solid #eee", flexShrink: 0 }}>
              <a
                href={geselecteerd.url} target="_blank" rel="noopener noreferrer"
                style={{ color: geselecteerd.kleur, fontWeight: "bold", textDecoration: "none" }}
              >
                Bezoek {geselecteerd.naam} →
              </a>
            </div>
          </div>

          <button
            onClick={e => { e.stopPropagation(); volgendeKrant(); }}
            style={pijlStijl}
            onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.30)"}
            onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.15)"}
          >›</button>
        </div>
      )}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
