"use client";

import {
  ActionIcon,
  Anchor,
  Box,
  Flex,
  Image,
  ScrollArea,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { Link } from "@tanstack/react-router";
import { useState } from "react";
import { FaGithub } from "react-icons/fa";
import { FiArrowRight, FiColumns } from "react-icons/fi";
import { SiJupyter } from "react-icons/si";
import { LOGO, PROJECT_NAME } from "@/const";

interface HomeSideBarProps {
  collapsed: boolean;
  toggle: () => void;
}

const HomeSideBar: React.FC<HomeSideBarProps> = ({ collapsed, toggle }) => {
  const [hovered, setHovered] = useState(false);

  return (
    <ScrollArea>
      <Stack>
        {/* Controls */}
        <Flex
          align="center"
          justify={collapsed ? "center" : "space-between"}
          px={collapsed ? "xs" : "md"}
        >
          {collapsed ? (
            <ActionIcon
              aria-label="Expand Sidebar"
              onMouseEnter={() => setHovered(true)}
              onMouseLeave={() => setHovered(false)}
              onClick={() => {
                toggle();
                setHovered(false);
              }}
              variant="subtle"
              h={32}
              w={32}
            >
              {hovered ? (
                <FiArrowRight aria-hidden="true" size={18} color="white" />
              ) : (
                <Image src={LOGO} alt="" h={25} w={25} />
              )}
            </ActionIcon>
          ) : (
            <>
              <Flex align="center" gap="xs">
                <Anchor underline="never" component={Link} to="/auth/login">
                  <Image
                    src={LOGO}
                    alt={`${PROJECT_NAME} Logo`}
                    h={32}
                    w={32}
                  />
                </Anchor>
              </Flex>
              <ActionIcon
                aria-label="Collapse Sidebar"
                onClick={toggle}
                variant="subtle"
                size="sm"
              >
                <FiColumns aria-hidden="true" size={18} color="white" />
              </ActionIcon>
            </>
          )}
        </Flex>
        {}
        {!collapsed && (
          <Box p={"md"} c="white">
            <Stack>
              <Title order={3}>About</Title>
              <Text>
                I wanted to learn how transformers work. To do this I
                implemented one using the JAX python library. This thought me
                about training, evelation, inference and new developements since
                the paper Attention is all you need.
              </Text>

              <Title order={3}>Model Architecture</Title>
              <Text>
                I used a standard encoder decoder architecture with a sequence
                length of 128, model dimension of 512, 8 attention heads, 6
                encoder decoder blocks and a feed forward dimension of 2048.
                This uses learned positional embeddings which is different from
                the original paper that uses fixed positional embeddings.
              </Text>

              <Title order={3}>Deployment</Title>
              <Text>
                To deploy the model I used Modal. The backend is hosted on flyio
                and the frontend is on cloudflare.
              </Text>
              <Anchor
                c="white"
                href={
                  "https://github.com/GaelGil/notebooks/blob/master/transformer/main.py"
                }
                target="_blank"
                rel="noopener noreferrer"
                className="flex hover:text-primary-600"
              >
                <Flex align="center" gap="xs">
                  <FaGithub size={24} />
                  <Text>GitHub</Text>
                </Flex>
              </Anchor>
              <Anchor
                c="white"
                href={
                  "https://github.com/GaelGil/notebooks/blob/master/transformer/transformers.ipynb"
                }
                target="_blank"
                rel="noopener noreferrer"
                className="flex hover:text-primary-600"
              >
                <Flex align="center" gap="xs">
                  <SiJupyter size={24} />
                  <Text>Jupyter</Text>
                </Flex>
              </Anchor>
            </Stack>
          </Box>
        )}
      </Stack>
    </ScrollArea>
  );
};

export default HomeSideBar;
