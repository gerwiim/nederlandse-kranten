const { useState, useEffect } = React;

const now = new Date();
const vandaag = [
  now.getFullYear(),
  String(now.getMonth() + 1).padStart(2, "0"),
  String(now.getDate()).padStart(2, "0"),
].join("-");

// Vaste gegevens per krant. De voorpagina's zelf komen uit archive.json,
// dat twee keer per dag door fetch_covers.py wordt bijgewerkt.
const krantenMeta = [
  { naam: "Algemeen Dagblad",       url: "https://www.ad.nl/",         kleur: "#E2001A" },
  { naam: "Nederlands Dagblad",     url: "https://www.nd.nl/",         kleur: "#005B8E" },
  { naam: "NRC",                    url: "https://www.nrc.nl/",        kleur: "#003082" },
  { naam: "Het Parool",             url: "https://www.parool.nl/",     kleur: "#1A1A1A" },
  { naam: "Reformatorisch Dagblad", url: "https://www.rd.nl/",         kleur: "#2E5E2E" },
  { naam: "De Telegraaf",           url: "https://www.telegraaf.nl/",  kleur: "#E30613" },
  { naam: "Trouw",                  url: "https://www.trouw.nl/",      kleur: "#E87722" },
  { naam: "de Volkskrant",          url: "https://www.volkskrant.nl/", kleur: "#CC0000" },
];

// Het RD staat in hoge resolutie op digibron.nl. Die site laat zich niet als
// plaatje insluiten (beveiligingscontrole), maar opent wel in een eigen tabblad.
function hogeResolutieUrl(naam, datum) {
  if (naam !== "Reformatorisch Dagblad" || !datum) return null;
  const [j, m, d] = datum.split("-");
  return `https://www.digibron.nl/images/generated/reformatorisch-dagblad/katern-nieuws/${j}/${m}/${d}/1-large.jpg`;
}

function KrantAfbeelding({ src, alt, stijl, foutStijl }) {
  const [fout, setFout] = useState(false);
  useEffect(() => { setFout(false); }, [src]);
  if (fout || !src) {
    // Sommige bronnen (zoals digibron.nl) laten zich niet als plaatje insluiten,
    // maar openen wel als je de link zelf bezoekt. Bied die link dan aan.
    const extern = src && src.startsWith("http");
    return (
      <div style={foutStijl}>
        {extern ? (
          <a
            href={src} target="_blank" rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            style={{ color: "#555", fontWeight: "bold" }}
          >
            📰 Bekijk voorpagina ↗
          </a>
        ) : (
          <>⚠️ Voorpagina<br />niet beschikbaar</>
        )}
      </div>
    );
  }
  return <img src={src} alt={alt} style={stijl} onError={() => setFout(true)} />;
}

function formatDatum(dateStr) {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("nl-NL", { weekday: "long", day: "numeric", month: "long" });
}

function App() {
  const [index, setIndex] = useState(null);
  const [geselecteerdeDatum, setGeselecteerdeDatum] = useState(null);
  const [archief, setArchief] = useState(null);
  const [archiefFout, setArchiefFout] = useState(false);

  useEffect(() => {
    // Querystring voorkomt dat de browser een verouderde versie uit de cache toont.
    fetch(`archive.json?t=${Date.now()}`)
      .then(r => r.json())
      .then(data => {
        setArchief(data);
        const datums = Object.keys(data).sort().reverse();
        if (datums.length) setGeselecteerdeDatum(datums[0]);
      })
      .catch(() => setArchiefFout(true));
  }, []);

  const beschikbareDatums = archief ? Object.keys(archief).sort().reverse() : [];
  const dagData = (archief && geselecteerdeDatum && archief[geselecteerdeDatum]) || {};
  const kranten = archief && geselecteerdeDatum
    ? krantenMeta.map(k => ({ ...k, voorpagina: dagData[k.naam] || null }))
    : [];

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

  const kopDatum = geselecteerdeDatum
    ? new Date(geselecteerdeDatum + "T12:00:00").toLocaleDateString("nl-NL", {
        weekday: "long", year: "numeric", month: "long", day: "numeric",
      })
    : "";

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
          {geselecteerdeDatum === vandaag ? "Voorpagina's van vandaag" : "Voorpagina's"}{kopDatum && ` — ${kopDatum}`}
        </p>
      </div>

      {/* Datumkiezer */}
      <div style={{ padding: "0 32px", marginBottom: "28px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
        <span style={{ fontWeight: "bold", fontSize: "0.95rem", color: "#444" }}>Datum:</span>
        <select
          value={geselecteerdeDatum || ""}
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
          {archief || archiefFout ? "Geen voorpagina's beschikbaar voor deze datum." : "Laden…"}
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
            <div style={{
              padding: "14px 20px", borderTop: "1px solid #eee", flexShrink: 0,
              display: "flex", justifyContent: "flex-end", gap: "20px", flexWrap: "wrap",
            }}>
              {hogeResolutieUrl(geselecteerd.naam, geselecteerdeDatum) && (
                <a
                  href={hogeResolutieUrl(geselecteerd.naam, geselecteerdeDatum)}
                  target="_blank" rel="noopener noreferrer"
                  style={{ color: geselecteerd.kleur, fontWeight: "bold", textDecoration: "none" }}
                >
                  Bekijk in hoge resolutie ↗
                </a>
              )}
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
