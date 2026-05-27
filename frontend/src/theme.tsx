import type { CSSVariablesResolver } from "@mantine/core";
import { createTheme } from "@mantine/core";
export type colorScheme = "light" | "dark";

export const theme = createTheme({
  colors: {
    night: [
      "#f8fafc",
      "#e5e7eb",
      "#cbd5e1",
      "#94a3b8",
      "#64748b",
      "#334155",
      "#1e293b",
      "#171724",
      "#101018",
      "#07070a",
    ],
    violet: [
      "#f5f0ff",
      "#e9dcff",
      "#d5b9ff",
      "#bd8cff",
      "#a566ff",
      "#8b3dff",
      "#7327e6",
      "#5d1dbd",
      "#481794",
      "#321066",
    ],
  },
  primaryColor: "violet",
  defaultRadius: "md",
  focusRing: "auto",
});

export const cssVariablesResolver: CSSVariablesResolver = (theme) => ({
  variables: {
    "--app-bg": "#07070a",
    "--app-surface": "#101018",
    "--app-surface-elevated": "#171724",
    "--app-border": "rgba(255, 255, 255, 0.1)",
    "--app-text": "#f8fafc",
    "--app-text-muted": "#aeb4c2",
    "--app-text-subtle": "#747b8f",
    "--app-accent": theme.colors.violet[5],
    "--app-accent-hover": theme.colors.violet[4],
    "--app-focus-ring": "rgba(139, 61, 255, 0.55)",
  },
  light: {
    "--mantine-color-text-primary": theme.black,
    "--mantine-color-text-secondary": theme.colors.gray[6],
  },
  dark: {
    "--mantine-color-text-primary": "var(--app-text)",
    "--mantine-color-text-secondary": "var(--app-text-muted)",
  },
});
