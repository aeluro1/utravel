import {
  Text,
  Group,
  Button,
  Paper,
  createStyles,
  Divider
} from "@mantine/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faMinus, faPlus, faStar, faStarHalf } from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";
import { savedItemsContext } from "contexts/SavedItemsContext";
import ImageCarousel from "./ImageCarousel";


const useStyles = createStyles((theme) => ({
  cardContainer: {
    width: "100%",
    minWidth: "200px",
    height: "min-content",
    [theme.fn.largerThan("sm")]: {
      maxWidth: "550px"
    },
    [theme.fn.smallerThan("sm")]: {
      maxWidth: "350px"
    }
  },
  card: {
    display: "grid",
    justifyContent: "center",
    gap: [theme.spacing.md],
    gridAutoRows: "160px",
    [theme.fn.largerThan("sm")]: {
      // gridAutoFlow: "row",
      // gridTemplateRows: "140px",
      gridTemplateColumns: "1fr 250px",
      gridTemplateAreas: '"cardInfo cardImage"'
    },
    [theme.fn.smallerThan("sm")]: {
      // gridAutoFlow: "column",
      // gridTemplateRows: "140px 160px", // Overrides auto row height if desired
      gridTemplateColumns: "1fr",
      gridTemplateAreas: '"cardInfo" "cardImage"'
    }
  },
  cardImageContainer: {
    gridArea: "cardImage",
    width: "100%",
    height: "100%",
    overflow: "hidden",
    minWidth: "0", // Prevents grid blowout
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
    gridArea: "cardInfo",
    display: "flex",
    flexFlow: "column nowrap",
    width: "100%",
    minWidth: "0", // Prevents grid blowout
  },
  cardInfoBtns: {
    marginTop: "auto",
    flexWrap: "nowrap"
  },
  actionBtn: {
    width: "90px"
  }
}));

export default function TableEntry({ item }) {
  const { classes } = useStyles();
  const { savedItems, addItem, delItem } = useContext(savedItemsContext);

  return (
    <Paper className={classes.cardContainer} shadow="xs" p="sm">
      <div className={classes.card}>
        <div className={classes.cardInfo}>
          <Text fz="md" truncate>{item.name}</Text>
          <Divider />
          <Group spacing="sm">
            <Text fz="sm">
              {[...Array(Math.max(Math.floor(item.rating), 0))].map((_, idx) => <FontAwesomeIcon key={idx} icon={faStar} />)}
              {item.rating % 1 === 0 ? null : <FontAwesomeIcon icon={faStarHalf} />}
              {[...Array(5 - Math.max(Math.ceil(item.rating), 0))].map((_, idx) => <FontAwesomeIcon key={idx} icon={faStar} style={{visibility: "hidden"}} />)}
            </Text>
            <Text fz="sm">
              {`${item.review_count}`}
            </Text>
          </Group>
          <Text fz="sm" truncate>{item.phone}</Text>
          <Text fz="sm" truncate>{item.address}</Text>
          <Text fz="sm" fs="italic" truncate>{item.tags.join(", ")}</Text>
          <Group spacing="sm" className={classes.cardInfoBtns}>
            {savedItems.some((i) => (i.id === item.id)) ? (
              <Button
                className={classes.actionBtn}
                compact
                leftIcon={<FontAwesomeIcon icon={faMinus} />}
                color="red"
                onClick={() => delItem(item.id)}
              >
                Delete
              </Button>
            ) : (
              <Button
                className={classes.actionBtn}
                compact
                leftIcon={<FontAwesomeIcon icon={faPlus} />}
                color="green"
                onClick={() => addItem(item)}
              >
                Save
              </Button>
            )}
            <Button
              className={classes.actionBtn}
              component="a"
              href={item.url}
              target="_blank"
              rel="noreferrer noopener"
              compact
              leftIcon={<FontAwesomeIcon icon={faEye} />}
              variant="light"
            >
              View
            </Button>
          </Group>
        </div>
        <div className={classes.cardImageContainer}>
          <ImageCarousel urls={item.imgs} alt={item.name} />
          {/* <img className={classes.cardImage} src={item.imgs[0]} alt={item.name} /> */}
        </div>
      </div>
    </Paper>
  );
}