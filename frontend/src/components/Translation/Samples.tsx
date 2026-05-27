"use client";

import {
  Accordion,
  Box,
  Button,
  Flex,
  ScrollArea,
  Stack,
  Text,
} from "@mantine/core";
import { FiHelpCircle } from "react-icons/fi";

import { useTranslationContext } from "@/contexts/TranslationContext";

interface PromptExample {
  text: string;
}

const SENTENCES: PromptExample[] = [
  {
    text: "Hola, ¿cómo estás?",
  },
  {
    text: "Buenos días, ¿qué tal dormiste?",
  },
  {
    text: "Me llamo María y soy de Mexico.",
  },
  {
    text: "¿Dónde está la biblioteca?",
  },
  {
    text: "Tengo hambre, vamos a comer algo.",
  },
  {
    text: "¿Puedes ayudarme con esta tarea?",
  },
  {
    text: "Mi libro favorito es 'Cien años de soledad'.",
  },
  {
    text: "Vamos al cine mañana por la noche.",
  },
  {
    text: "El español es un idioma muy hermoso.",
  },
];

const Samples = () => {
  const { setSrc } = useTranslationContext();

  return (
    <Accordion>
      <Accordion.Item value="how-to-prompt">
        <Accordion.Control bg="transparent">
          <Flex align="center" gap="xs" c="var(--app-text)">
            <FiHelpCircle aria-hidden="true" size={16} />
            <Text size="sm" fw={500}>
              Sample Spanish Sentences
            </Text>
          </Flex>
        </Accordion.Control>
        <Accordion.Panel>
          <Box p="xs">
            <ScrollArea.Autosize h={200}>
              <Stack gap="xs">
                {SENTENCES.map((example, index) => (
                  <Button
                    key={index}
                    aria-label={`Use Sample Sentence ${index + 1}`}
                    justify="flex-start"
                    p="xs"
                    variant="subtle"
                    style={{
                      borderRadius: 6,
                      border: "1px solid var(--app-border)",
                      backgroundColor: "var(--app-surface-elevated)",
                      height: "auto",
                      transition:
                        "border-color 0.2s ease, background-color 0.2s ease",
                    }}
                    onClick={() => setSrc(example.text)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor =
                        "var(--app-accent)";
                      e.currentTarget.style.backgroundColor =
                        "var(--app-surface)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor =
                        "var(--app-border)";
                      e.currentTarget.style.backgroundColor =
                        "var(--app-surface-elevated)";
                    }}
                  >
                    <Flex justify="space-between" align="flex-start">
                      <Box style={{ flex: 1, overflow: "hidden" }}>
                        <Text size="xs" lineClamp={2} c="var(--app-text-muted)">
                          {example.text}
                        </Text>
                      </Box>
                    </Flex>
                  </Button>
                ))}
              </Stack>
            </ScrollArea.Autosize>
          </Box>
        </Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
};

export default Samples;
