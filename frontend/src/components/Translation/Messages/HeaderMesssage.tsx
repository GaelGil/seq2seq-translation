import { Box, Title } from "@mantine/core"

const HeaderMessage = () => {
  return (
    <Box maw={720} ta="center">
      <Title order={1} fw={300} c="var(--app-text)" style={{ textWrap: "balance" }}>
        Translate Spanish Into English
      </Title>
    </Box>
  )
}

export default HeaderMessage
