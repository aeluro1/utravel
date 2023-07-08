import {
  Text,
  Group,
  Image,
  Button,
  Paper,
  rem,
  createStyles,
  Flex
} from "@mantine/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faPlus } from "@fortawesome/free-solid-svg-icons";


export default function TableEntry({ item }) {

  // const useStyles = createStyles((theme) => ({
  //   button: {
  //     paddingLeft: rem(20),
  //     paddingRight: rem(20)
  //   }
  // }))
  
  // switch (item.type) {
  //   case "restaurant":

  // }
  return (
    <Paper shadow="xs" p="sm">
      <Flex
        justify="space-between"
        align="center"
        direction="row"
        wrap="wrap"
      >
        <div>
          <Text>{item.name}</Text>
          <Text>{item.phone}</Text>
          <Text>{item.address}</Text>
          <Group spacing="sm">
            <Button
              leftIcon={<FontAwesomeIcon icon={faPlus} />}
            >
              Save
            </Button>
            <Button
              component="a"
              href={item.url}
              target="_blank"
              rel="noreferrer noopener"
              leftIcon={<FontAwesomeIcon icon={faEye} />}
            >
              View
            </Button>
          </Group>
        </div>
        <div>
          <Image width={200} height={100} mx="auto" radius="md" src={item.imgs[0]} alt={item.name} />
        </div>
      </Flex>
    </Paper>
  )
}