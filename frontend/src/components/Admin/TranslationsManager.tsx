"use client";

import { Container, Flex, Switch, Table, Text } from "@mantine/core";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { TranslationService } from "@/client";
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination";
import PendingTranslations from "@/components/Pending/PendingTranslations";

const PER_PAGE = 10;

function TranslationsManager() {
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryFn: () => TranslationService.getTranslationsAdmin(),
    queryKey: ["translations"],
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: boolean }) =>
      TranslationService.setSubmissionStatus({
        requestBody: { id, new_status: status },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["translations"] });
    },
  });

  const allTranslations = data?.translations ?? [];
  const count = allTranslations.length;
  const totalPages = Math.ceil(count / PER_PAGE);

  const startIdx = (page - 1) * PER_PAGE;
  const translations = allTranslations.slice(startIdx, startIdx + PER_PAGE);

  if (isLoading) {
    return <PendingTranslations />;
  }

  return (
    <Container p={0}>
      <Table verticalSpacing="sm" highlightOnHover striped>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Source</Table.Th>
            <Table.Th>Translation</Table.Th>
            <Table.Th>Correct</Table.Th>
            <Table.Th>Incorrect</Table.Th>
            <Table.Th>Public</Table.Th>
            <Table.Th>Set Status</Table.Th>
          </Table.Tr>
        </Table.Thead>

        <Table.Tbody>
          {translations.length === 0 && (
            <Table.Tr>
              <Table.Td colSpan={6}>
                <Text c="dimmed">No translations found</Text>
              </Table.Td>
            </Table.Tr>
          )}

          {translations.map((t, idx) => (
            <Table.Tr key={startIdx + idx}>
              <Table.Td style={{ maxWidth: 300 }}>
                <Text lineClamp={2}>{t.src}</Text>
              </Table.Td>
              <Table.Td style={{ maxWidth: 300 }}>
                <Text lineClamp={2}>{t.translation || "—"}</Text>
              </Table.Td>
              <Table.Td style={{ maxWidth: 300 }}>
                <Text lineClamp={2}>{t.correct ?? "—"}</Text>
              </Table.Td>
              <Table.Td style={{ maxWidth: 300 }}>
                <Text lineClamp={2}>{t.incorrect ?? "—"}</Text>
              </Table.Td>
              <Table.Td style={{ maxWidth: 100 }}>
                <Text>{t.public_status ? "Yes" : "No"}</Text>
              </Table.Td>
              <Table.Td style={{ maxWidth: 100 }}>
                <Switch
                  checked={t.public_status}
                  onChange={() =>
                    updateStatusMutation.mutate({
                      id: t.id,
                      status: !t.public_status,
                    })
                  }
                  disabled={updateStatusMutation.isPending}
                />
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>

      {totalPages > 1 && (
        <Flex mt={4} justify="center">
          <PaginationRoot
            page={page}
            totalPages={totalPages}
            count={count}
            pageSize={PER_PAGE}
            onPageChange={setPage}
          >
            <Flex gap="sm" align="center">
              <PaginationPrevTrigger />
              <PaginationItems />
              <PaginationNextTrigger />
            </Flex>
          </PaginationRoot>
        </Flex>
      )}
    </Container>
  );
}

export default TranslationsManager;
