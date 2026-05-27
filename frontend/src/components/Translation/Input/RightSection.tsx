import { Button } from "@mantine/core"
import { FaSquare } from "react-icons/fa"
import { FiArrowUp } from "react-icons/fi"
import { useTranslationContext } from "@/contexts/TranslationContext"

const RightSection: React.FC = () => {
  const { src, isSubmitting, isValid, isStreaming } = useTranslationContext()
  if (!src || isSubmitting || isStreaming) return null

  return (
    <Button
      aria-label="Translate Text"
      type="submit"
      disabled={!isValid}
      radius="xl"
      bg={isSubmitting ? "gray" : "none"}
    >
      {isSubmitting ? (
        <FaSquare aria-hidden="true" size={15} color="white" />
      ) : (
        <FiArrowUp aria-hidden="true" size={15} color="white" />
      )}
    </Button>
  )
}

export default RightSection
