import { Carousel } from "@mantine/carousel";
import { createStyles } from "@mantine/core";


const useStyles = createStyles((theme) => ({
  container: {
    height: "100%",
    width: "100%",
    display: "flex"
  },
  cardImage: {
    objectFit: "cover",
    height: "100%",
    width: "100%",
    borderRadius: [theme.radius.md]
  }
}));

export default function ImageCarousel({ urls, alt }) {
  const { classes } = useStyles();

  return (
    <div className={classes.container}>
      <Carousel withIndicators height="100%" sx={{ flex: 1 }}>
        {urls.map((url) => (
          <Carousel.Slide key={url}><img className={classes.cardImage} src={url} alt={alt} /></Carousel.Slide>
        ))}
      </Carousel>
    </div>
  );
}