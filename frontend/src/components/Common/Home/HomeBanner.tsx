import { Anchor, Box, Container, Stack, Text, Title } from "@mantine/core"
import { Link } from "@tanstack/react-router"
import { PROJECT_NAME } from "@/const"
import { Button } from "../../../components/ui/button"

const HomeBanner = () => {
  const today = new Date().toLocaleDateString()
  return (
    <Container size="lg">
      <Stack align="center" gap="xl" mt={80}>
        <Box ta="center">
          <Title order={1} fw={700} mb={4} c="var(--app-text)">
            {PROJECT_NAME}
          </Title>

          <Text fz="sm" c="var(--app-text-muted)" mb="lg">
            {today}
          </Text>

          <Anchor component={Link} underline="never" to="/chat">
            <Button radius="xl" size="lg" variant="outline" px="xl">
              Get Started
            </Button>
          </Anchor>
        </Box>

        {/* Main content */}
        <Box maw={720} ta="center">
          <Title order={2} mb="md" fw={600} c="var(--app-text)">
            Lorem ipsum dolor sit amet consectetur adipisicing elit.
          </Title>

          <Text fz="lg" c="var(--app-text-muted)" lh={1.6}>
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Itaque,
            quaerat minima ducimus doloribus dolore, inventore impedit iste
            maxime temporibus earum beatae tenetur quisquam enim reprehenderit
            rem necessitatibus eaque omnis deserunt.
          </Text>
        </Box>
      </Stack>
    </Container>
  )
}

export default HomeBanner
