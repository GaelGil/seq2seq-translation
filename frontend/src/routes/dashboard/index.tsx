import { ActionIcon, Container, Flex, Tabs, Title } from "@mantine/core";

import { createFileRoute, Link } from "@tanstack/react-router";
import type { ComponentType, ReactNode } from "react";
import {
  FaEye,
  FaHome,
  FaLanguage,
  FaLock,
  FaSun,
  FaUser,
} from "react-icons/fa";

import useAuth from "@/hooks/useAuth";
import TranslationsManager from "@/components/Admin/TranslationsManager";
import UserInformation from "@/components/UserSettings/UserInformation";
import ChangePassword from "@/components/UserSettings/ChangePassword";
import Appearance from "@/components/UserSettings/Appearance";
import DeleteAccount from "@/components/UserSettings/DeleteAccount";

type DashboardSearch = {
  tab?: string;
};

type DashboardTab = {
  value: string;
  title: string;
  icon: ReactNode;
  component: ComponentType | null;
  adminOnly?: boolean;
};

export const Route = createFileRoute("/dashboard/")({
  validateSearch: (search: Record<string, unknown>): DashboardSearch => ({
    tab: typeof search.tab === "string" ? search.tab : undefined,
  }),
  component: Dashboard,
});

const tabsConfig: DashboardTab[] = [
  {
    value: "home",
    title: "Home",
    icon: <FaUser aria-hidden="true" />,
    component: null,
  },
  {
    value: "profile",
    title: "My Profile",
    icon: <FaUser aria-hidden="true" />,
    component: UserInformation,
  },
  {
    value: "password",
    title: "Password",
    icon: <FaLock aria-hidden="true" />,
    component: ChangePassword,
  },
  {
    value: "appearance",
    title: "Appearance",
    icon: <FaSun aria-hidden="true" />,
    component: Appearance,
  },
  {
    value: "translations",
    title: "Translations",
    icon: <FaLanguage aria-hidden="true" />,
    component: TranslationsManager,
    adminOnly: true,
  },
  {
    value: "danger-zone",
    title: "Danger Zone",
    icon: <FaEye aria-hidden="true" />,
    component: DeleteAccount,
  },
];

function Dashboard() {
  const { user: currentUser } = useAuth();
  const { tab } = Route.useSearch();
  const navigate = Route.useNavigate();

  const isSuperuser = currentUser?.is_superuser;

  const tabs = isSuperuser
    ? tabsConfig
    : tabsConfig.filter((tab) => !tab.adminOnly);
  const activeTab = tabs.some((item) => item.value === tab) ? tab : "home";

  const setActiveTab = (value: string | null) => {
    const nextTab = value ?? "home";

    navigate({
      search: (previous) => ({
        ...previous,
        tab: nextTab === "home" ? undefined : nextTab,
      }),
    });
  };

  return (
    <Container size="lg" py="xl">
      <Flex align="center" gap="md" mb="lg">
        <ActionIcon
          aria-label="Go Home"
          component={Link}
          to="/"
          variant="subtle"
          size="lg"
        >
          <FaHome aria-hidden="true" size={20} />
        </ActionIcon>
        <Title order={1} size="h2" style={{ textWrap: "balance" }}>
          Dashboard
        </Title>
      </Flex>

      <Tabs value={activeTab} onChange={setActiveTab} variant="subtle">
        <Tabs.List
          style={{
            flexWrap: "nowrap",
            overflowX: "auto",
            scrollbarWidth: "thin",
          }}
        >
          {tabs.map((tab) => (
            <Tabs.Tab
              key={tab.value}
              leftSection={tab.icon}
              value={tab.value}
              fw={activeTab === tab.value ? "800" : "normal"}
              size="xl"
            >
              {tab.title}
            </Tabs.Tab>
          ))}
        </Tabs.List>

        {tabs.map((tab) => (
          <Tabs.Panel key={tab.value} value={tab.value} pt="lg">
            {tab.component ? <tab.component /> : null}
          </Tabs.Panel>
        ))}
      </Tabs>
    </Container>
  );
}
