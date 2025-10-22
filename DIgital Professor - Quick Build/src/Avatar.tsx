import { useEffect, useState } from "react";
import classNames from "classnames";
import "./Avatar.scss";

export default function Avatar() {
  const [speaking, setSpeaking] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const onMsg = (e: any) => {
      const m = e.detail;
      if (
        m?.serverContent?.modelTurn?.parts?.some((p: any) =>
          p.inlineData?.mimeType?.startsWith("audio/")
        )
      ) {
        setSpeaking(true);
        setIsOpen(true);
      }
      if (m?.serverContent?.turnComplete || m?.serverContent?.generationComplete) {
        setSpeaking(false);
      }
    };
    window.addEventListener("gemini:serverMessage", onMsg as any);
    return () => window.removeEventListener("gemini:serverMessage", onMsg as any);
  }, []);

  const handleBackdropClick = (event: React.MouseEvent<HTMLElement>) => {
    if (event.target === event.currentTarget) {
      setIsOpen(false);
    }
  };

  return (
    <>
      <button
        className="prof-avatar__toggle"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-pressed={isOpen}
      >
        {isOpen ? "Close" : "View Avatar"}
      </button>

      {isOpen && (
        <figure
          className={classNames("prof-avatar", {
            "is-speaking": speaking,
          })}
          role="img"
          aria-label={
            speaking
              ? "Professor Neil Morgan avatar gesturing while speaking"
              : "Professor Neil Morgan avatar"
          }
          onMouseDown={handleBackdropClick}
        >
          <div className="prof-avatar__card" role="presentation">
            <div className="prof-avatar__stage">
              <div className="prof-avatar__shadow" aria-hidden />

              <div className="prof-avatar__figure" aria-hidden>
                <div className="prof-avatar__head">
                  <div className="prof-avatar__hair">
                    <div className="prof-avatar__hair-crown" />
                    <div className="prof-avatar__hair-side prof-avatar__hair-side--left" />
                    <div className="prof-avatar__hair-side prof-avatar__hair-side--right" />
                  </div>

                  <div className="prof-avatar__ear prof-avatar__ear--left">
                    <div className="prof-avatar__ear-inner" />
                  </div>
                  <div className="prof-avatar__ear prof-avatar__ear--right">
                    <div className="prof-avatar__ear-inner" />
                  </div>

                  <div className="prof-avatar__face">
                    <div className="prof-avatar__temple prof-avatar__temple--left" />
                    <div className="prof-avatar__temple prof-avatar__temple--right" />
                    <div className="prof-avatar__brow prof-avatar__brow--left" />
                    <div className="prof-avatar__brow prof-avatar__brow--right" />
                    <div className="prof-avatar__eye prof-avatar__eye--left">
                      <div className="prof-avatar__eye-iris" />
                    </div>
                    <div className="prof-avatar__eye prof-avatar__eye--right">
                      <div className="prof-avatar__eye-iris" />
                    </div>
                    <div className="prof-avatar__eye-highlight prof-avatar__eye-highlight--left" />
                    <div className="prof-avatar__eye-highlight prof-avatar__eye-highlight--right" />
                    <div className="prof-avatar__nose" />
                    <div className="prof-avatar__philtrum" />
                    <div className="prof-avatar__mouth">
                      <div className="prof-avatar__mouth-inner" />
                      <div className="prof-avatar__lip" />
                    </div>
                    <div className="prof-avatar__chin-highlight" />
                  </div>

                  <div className="prof-avatar__glasses">
                    <div className="prof-avatar__glasses-lens prof-avatar__glasses-lens--left" />
                    <div className="prof-avatar__glasses-bridge" />
                    <div className="prof-avatar__glasses-lens prof-avatar__glasses-lens--right" />
                  </div>
                </div>

                <div className="prof-avatar__neck" />
                <div className="prof-avatar__shoulders" />

                <div className="prof-avatar__torso">
                  <div className="prof-avatar__shirt" />
                  <div className="prof-avatar__shirt-seam" />
                  <div className="prof-avatar__placket" />
                  <div className="prof-avatar__button prof-avatar__button--top" />
                  <div className="prof-avatar__button prof-avatar__button--mid" />
                  <div className="prof-avatar__button prof-avatar__button--low" />
                  <div className="prof-avatar__pocket" />
                </div>

                <div className="prof-avatar__arm prof-avatar__arm--left">
                  <div className="prof-avatar__sleeve" />
                  <div className="prof-avatar__sleeve-roll" />
                  <div className="prof-avatar__forearm" />
                  <div className="prof-avatar__hand">
                    <div className="prof-avatar__finger prof-avatar__finger--thumb" />
                    <div className="prof-avatar__finger prof-avatar__finger--index" />
                    <div className="prof-avatar__finger prof-avatar__finger--middle" />
                  </div>
                  <div className="prof-avatar__watch">
                    <div className="prof-avatar__watch-face" />
                  </div>
                </div>

                <div className="prof-avatar__arm prof-avatar__arm--right">
                  <div className="prof-avatar__sleeve" />
                  <div className="prof-avatar__sleeve-roll" />
                  <div className="prof-avatar__forearm" />
                  <div className="prof-avatar__hand">
                    <div className="prof-avatar__finger prof-avatar__finger--thumb" />
                    <div className="prof-avatar__finger prof-avatar__finger--index" />
                    <div className="prof-avatar__finger prof-avatar__finger--middle" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </figure>
      )}
    </>
  );
}
