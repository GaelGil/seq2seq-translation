import { ActionIcon, Box, Textarea, Tooltip, Text } from "@mantine/core";
import { FiX } from "react-icons/fi";

import { useTranslationContext } from "@/contexts/TranslationContext";
import RightSection from "./RightSection";

const InputBar: React.FC = () => {
  const { src, setSrc, handleSubmit, isStreaming, isSubmitting, isValid } =
    useTranslationContext();

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        handleSubmit();
      }}
      style={{ flex: 1, display: "flex", flexDirection: "column" }}
    >
      <Box
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {!isValid && src !== "" && (
          <Text c="red">Text must be 3 words or more</Text>
        )}
        <Textarea
          id="translation-source"
          name="translation-source"
          style={{ flex: 1 }}
          c="white"
          variant="unstyled"
          placeholder="Example: Hola, ¿cómo estás?…"
          autoComplete="off"
          autosize
          minRows={6}
          maxRows={12}
          disabled={isStreaming || isSubmitting}
          value={src}
          onChange={(e) => setSrc(e.target.value)}
          styles={{ input: { color: "white" } }}
        />
        <Box
          style={{
            position: "absolute",
            bottom: 8,
            right: src && !isStreaming && !isSubmitting ? 40 : 8,
          }}
        >
          <RightSection />
        </Box>
        {src && !isStreaming && !isSubmitting && (
          <Box
            style={{
              position: "absolute",
              bottom: 8,
              right: 0,
            }}
          >
            <Tooltip label="Clear">
              <ActionIcon
                aria-label="Clear Source Text"
                variant="subtle"
                color="gray"
                onClick={() => setSrc("")}
                size="sm"
              >
                <FiX aria-hidden="true" size={16} color="red" />
              </ActionIcon>
            </Tooltip>
          </Box>
        )}
      </Box>
    </form>
  );
};

export default InputBar;
