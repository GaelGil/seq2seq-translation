"use client";

import * as React from "react";
import {
  ActionIcon,
  Skeleton,
  Box,
  useMantineColorScheme,
} from "@mantine/core";
import { LuMoon, LuSun } from "react-icons/lu";

export type ColorScheme = "light" | "dark";

export interface ColorModeProviderProps {
  initialColorScheme?: ColorScheme;
  children: React.ReactNode;
}

export function ColorModeProvider({
  initialColorScheme: _initialColorScheme = "dark",
  children,
}: ColorModeProviderProps) {
  return <>{children}</>;
}

export function useColorMode() {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();

  return {
    colorMode: colorScheme as ColorScheme,
    setColorMode: (mode: ColorScheme) => {
      if (mode !== colorScheme) toggleColorScheme();
    },
    toggleColorScheme,
  };
}

export function useColorModeValue<T>(light: T, dark: T) {
  const { colorMode } = useColorMode();
  return colorMode === "dark" ? dark : light;
}

export function ColorModeIcon() {
  const { colorMode } = useColorMode();
  return colorMode === "dark" ? (
    <LuMoon aria-hidden="true" />
  ) : (
    <LuSun aria-hidden="true" />
  );
}

export const ColorModeButton = React.forwardRef<
  HTMLButtonElement,
  React.ComponentProps<typeof ActionIcon>
>(function ColorModeButton(props, ref) {
  const { toggleColorScheme } = useColorMode();
  return (
    <React.Suspense fallback={<Skeleton width={32} height={32} />}>
      <ActionIcon
        aria-label="Toggle Color Scheme"
        onClick={toggleColorScheme}
        variant="light"
        size="sm"
        ref={ref}
        {...props}
      >
        <ColorModeIcon />
      </ActionIcon>
    </React.Suspense>
  );
});

export const LightMode = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>(function LightMode(props, ref) {
  return (
    <Box
      component="span"
      ref={ref}
      {...props}
      style={{ display: "contents" }}
      className="mantine-theme light"
    />
  );
});

export const DarkMode = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>(function DarkMode(props, ref) {
  return (
    <Box
      component="span"
      ref={ref}
      {...props}
      style={{ display: "contents" }}
      className="mantine-theme dark"
    />
  );
});
