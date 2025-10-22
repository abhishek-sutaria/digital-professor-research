import { useCallback, useEffect, useState } from "react";
import Select from "react-select";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";
import { Modality } from "@google/genai";

const responseOptions = [
  { value: "audio", label: "audio" },
  { value: "text", label: "text" },
];

export default function ResponseModalitySelector() {
  const { config, setConfig } = useLiveAPIContext();

  // Load from localStorage or default to audio
  const [selectedOption, setSelectedOption] = useState<{
    value: string;
    label: string;
  } | null>(() => {
    const saved = localStorage.getItem("gemini-response-modality");
    return saved === "text" ? responseOptions[1] : responseOptions[0];
  });

  const updateConfig = useCallback(
    (modality: "audio" | "text") => {
      // Save to localStorage
      localStorage.setItem("gemini-response-modality", modality);

      const desiredModality =
        modality === "audio" ? Modality.AUDIO : Modality.TEXT;
      const currentModality = config.responseModalities?.[0];

      if (currentModality === desiredModality) {
        return;
      }

      setConfig({
        ...config,
        responseModalities: [desiredModality],
      });
    },
    [config, setConfig]
  );

  // Set initial modality on mount
  useEffect(() => {
    if (selectedOption) {
      updateConfig(selectedOption.value as "audio" | "text");
    }
  }, [selectedOption, updateConfig]);

  return (
    <div className="select-group">
      <label htmlFor="response-modality-selector">Response modality</label>
      <Select
        id="response-modality-selector"
        className="react-select"
        classNamePrefix="react-select"
        styles={{
          control: (baseStyles) => ({
            ...baseStyles,
            background: "var(--Neutral-15)",
            color: "var(--Neutral-90)",
            minHeight: "33px",
            maxHeight: "33px",
            border: 0,
          }),
          option: (styles, { isFocused, isSelected }) => ({
            ...styles,
            backgroundColor: isFocused
              ? "var(--Neutral-30)"
              : isSelected
              ? "var(--Neutral-20)"
              : undefined,
          }),
        }}
        defaultValue={selectedOption}
        options={responseOptions}
        onChange={(e) => {
          setSelectedOption(e);
          if (e && (e.value === "audio" || e.value === "text")) {
            updateConfig(e.value);
          }
        }}
      />
    </div>
  );
}
