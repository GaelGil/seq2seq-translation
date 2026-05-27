import { Box, Container, Loader, Textarea } from "@mantine/core"

const LoadingMessages = () => {
  return (
    <Container
      fluid
      style={{ display: "flex", flexDirection: "column" }}
      w="75%"
      h="100%"
    >
      <Box
        style={{
          flex: 1,
          alignItems: "center",
          justifyContent: "center",
        }}
        px="md"
        w="100%"
        display={"flex"}
      >
        <Loader size="md" color="var(--app-text)" />
      </Box>

      <Box w="100%" bottom={0} pos={"sticky"} p="md">
        <Textarea
          placeholder="Ask Anything"
          radius="xl"
          autosize
          w="100%"
          size="lg"
          disabled
        />
      </Box>
    </Container>
  )
}

export default LoadingMessages
