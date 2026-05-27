"use client";

import {
  Accordion,
  Box,
  Flex,
  ScrollArea,
  Stack,
  Text,
} from "@mantine/core";
import { FiHelpCircle } from "react-icons/fi";
import { TranslationService } from "@/client";
import { useQuery } from "@tanstack/react-query";

function getUserSubmissions() {
  return {
    queryFn: () => TranslationService.getTranslationsPublic(),
    queryKey: ["userSubmisions"],
  };
}

const UserSubmisions = () => {
  const {
    data: userSubmissions,
    isLoading,
    isError,
  } = useQuery({
    ...getUserSubmissions(),
  });

  const translations = userSubmissions?.translations;

  return (
    <Accordion>
      <Accordion.Item value="how-to-prompt">
        <Accordion.Control bg="transparent">
          <Flex align="center" gap="xs" c="white">
            <FiHelpCircle aria-hidden="true" size={16} color="white" />
            <Text size="sm" fw={500}>
              User Submissions
            </Text>
          </Flex>
        </Accordion.Control>
        <Accordion.Panel>
          <Box p="xs">
            <ScrollArea.Autosize>
              {isLoading ? (
                <Text aria-live="polite">Loading…</Text>
              ) : isError ? (
                <Text c="red">Error loading translations</Text>
              ) : translations?.length === 0 ? (
                <Text>Nothing here yet</Text>
              ) : (
                <Stack gap="md">
                  {translations?.map((example, index) => (
                    <Box
                      key={index}
                      p="sm"
                      style={{
                        borderRadius: 8,
                        border: "1px solid var(--mantine-color-dark-5)",
                        backgroundColor: "var(--mantine-color-dark-6)",
                      }}
                    >
                      <Box mb="xs">
                        <Text size="xs" c="dimmed" mb={4}>
                          Source
                        </Text>
                        <Text size="sm" c="gray.2">
                          {example.src}
                        </Text>
                      </Box>
                      <Box
                        pt="xs"
                        style={{
                          borderTop: "1px dashed var(--mantine-color-dark-4)",
                        }}
                      >
                        <Text size="xs" c="teal" mb={4}>
                          Translation
                        </Text>
                        <Text size="sm" c="gray.2">
                          {example.translation}
                        </Text>
                      </Box>
                    </Box>
                  ))}
                </Stack>
              )}
            </ScrollArea.Autosize>
          </Box>
        </Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
};

export default UserSubmisions;
