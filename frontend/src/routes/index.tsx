import {
  AppShell,
  Box,
  Container,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Text,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { createFileRoute } from "@tanstack/react-router";
import InputBar from "@/components/Translation/Input/InputBar";
import HeaderMessage from "@/components/Translation/Messages/HeaderMesssage";
import Translation from "@/components/Translation/Messages/Translation";
import Samples from "@/components/Translation/Samples";
import UserSubmisions from "@/components/Translation/UserSubmissions";
import { TranslationProvider } from "@/contexts/TranslationContext";
import HomeSideBar from "../components/Common/Home/HomeSideBar";
export const Route = createFileRoute("/")({
  component: HomePage,
});

const panelStyle = {
  backgroundColor: "var(--mantine-color-dark-8)",
  border: "1px solid var(--mantine-color-dark-5)",
  height: "100%",
  display: "flex",
  flexDirection: "column" as const,
};

function HomePage() {
  const [collapsed, { toggle: toggleCollapsed }] = useDisclosure(false);

  const fullWidth = 350;
  const collapsedWidth = 60;

  const sidebarWidth = collapsed ? collapsedWidth : fullWidth;

  return (
    <TranslationProvider>
      <AppShell
        layout="alt"
        navbar={{
          width: sidebarWidth,
          breakpoint: "sm",
          collapsed: { mobile: true, desktop: false },
        }}
        padding="md"
        bg="dark.9"
      >
        <AppShell.Navbar p="md" withBorder={false} bg="dark.9">
          <HomeSideBar collapsed={collapsed} toggle={toggleCollapsed} />
        </AppShell.Navbar>
        <AppShell.Main>
          <Container
            id="main-content"
            fluid
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              minHeight: "calc(100svh - var(--app-shell-padding))",
              paddingBottom: "max(10vh, env(safe-area-inset-bottom))",
              overflowX: "hidden",
            }}
          >
            <Stack w="100%" maw={1080} gap="lg">
              <Box ta="center">
                <HeaderMessage />
              </Box>
              <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                <Box c="white" style={{ minWidth: 0 }}>
                  <Paper p="md" radius="lg" style={panelStyle}>
                    <Text
                      component="label"
                      htmlFor="translation-source"
                      size="sm"
                      fw={500}
                      mb="xs"
                    >
                      Spanish
                    </Text>
                    <InputBar />
                  </Paper>
                </Box>

                <Box style={{ minWidth: 0 }}>
                  <Paper p="md" radius="lg" style={panelStyle}>
                    <Select
                      label="Output Language"
                      placeholder="Choose Output Language…"
                      data={["English"]}
                      defaultValue="English"
                      mb="md"
                      variant="filled"
                      styles={{ input: { color: "white" } }}
                    />
                    <Translation />
                  </Paper>
                </Box>
              </SimpleGrid>
              <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                <Box style={{ minWidth: 0 }}>
                  <Samples />
                </Box>
                <Box style={{ minWidth: 0 }}>
                  <UserSubmisions />
                </Box>
              </SimpleGrid>
            </Stack>
          </Container>
        </AppShell.Main>
      </AppShell>
    </TranslationProvider>
  );
}
