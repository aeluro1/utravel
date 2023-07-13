import {
  Text,
  Group,
  Button,
  Paper,
  createStyles,
  Divider
} from "@mantine/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faPlus, faStar, faStarHalf } from "@fortawesome/free-solid-svg-icons";


const useStyles = createStyles((theme) => ({
  cardContainer: {
    [theme.fn.largerThan("xs")]: {
      width: "min(600px, 80%)"
    },
    [theme.fn.smallerThan("xs")]: {
      width: "80%"
    }
  },
  card: {
    display: "grid",
    justifyContent: "center",
    gap: [theme.spacing.md],
    [theme.fn.largerThan("xs")]: {
      height: "140px",
      gridAutoFlow: "row",
      gridTemplateRows: "1fr",
      // gridTemplateColumns: "minmax(0, 2fr) minmax(0, 1fr)", // To prevent grid blowout if using fr units
      gridTemplateColumns: "2fr 200px"
    },
    [theme.fn.smallerThan("xs")]: {
      gridAutoFlow: "column",
      gridTemplateRows: "150px 150px",
      gridTemplateColumns: "1fr"
    },
    "> div": {
      outline: "1px solid red"
    }
  },
  cardImageContainer: {
    width: "100%",
    height: "100%",
    overflow: "hidden",
    minWidth: "0", // Prevents grid blowout
    // minHeight: "0",
    textAlign: "center"
  },
  cardImage: {
    objectFit: "cover",
    width: "100%",
    height: "100%",
    maxWidth: "250px",
    borderRadius: "10%",
  },
  cardInfo: {
    display: "flex",
    flexFlow: "column nowrap",
    width: "100%",
    minWidth: "0", // Prevents grid blowout
    // minHeight: "0"
  },
  cardInfoBtns: {
    marginTop: "auto"
  }
}))

export default function TableEntry({ item }) {
  const { classes, cx } = useStyles();
  return (
    <Paper className={classes.cardContainer} shadow="xs" p="sm">
      <div className={classes.card}>
        <div className={classes.cardInfo}>
          <Text fz="md" truncate>{item.name}</Text>
          <Divider />
          <Group spacing="sm">
            <Text fz="sm">
              {[...Array(Math.floor(item.rating))].map(() => <FontAwesomeIcon icon={faStar} />)}
              {[...Array(5 - Math.ceil(item.rating))].map(() => <FontAwesomeIcon icon={faStar} style={{visibility: "hidden"}} />)}
              {item.rating % 1 === 0 ? null : <FontAwesomeIcon icon={faStarHalf} />}
            </Text>
            <Text fz="sm">
              {`${item.review_count}`}
            </Text>
          </Group>
          
          <Text fz="sm" truncate>{item.phone}</Text>
          <Text fz="sm" truncate>{item.address}</Text>
          <Group spacing="sm" className={classes.cardInfoBtns}>
            <Button
              compact
              leftIcon={<FontAwesomeIcon icon={faPlus} />}
            >
              Save
            </Button>
            <Button
              compact
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
        <div className={classes.cardImageContainer}>
          <img className={classes.cardImage} src={item.imgs[0]} alt={item.name} />
        </div>
      </div>
    </Paper>
  )
}