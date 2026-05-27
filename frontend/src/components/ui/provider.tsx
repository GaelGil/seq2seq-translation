"use client";

import { type PropsWithChildren } from "react";
import { ColorModeProvider } from "./color-mode";
import { Toaster } from "./toaster";
import "@mantine/core/styles.css";
import { cssVariablesResolver, theme } from "../../theme";
import { MantineProvider } from "@mantine/core";

export function CustomProvider(props: PropsWithChildren) {
  return (
    <MantineProvider
      theme={theme}
      cssVariablesResolver={cssVariablesResolver}
      defaultColorScheme="dark"
    >
      <ColorModeProvider initialColorScheme="dark">
        {props.children}
      </ColorModeProvider>
      <Toaster />
    </MantineProvider>
  );
}
