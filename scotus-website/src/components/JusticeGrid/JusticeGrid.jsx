import JusticeVoteRow from "@/components/JusticeVoteRow/JusticeVoteRow";
import styles from "./JusticeGrid.module.css";

export default function JusticeGrid({ justiceVotes, predictedOutcome }) {
  return (
    <div className={styles.wrapper}>
      {predictedOutcome && (
        <div className={styles.outcomeBox}>
          <div className={styles.outcomeLabel}>Predicted Outcome</div>
          <div className={styles.outcomeText}>{predictedOutcome}</div>
        </div>
      )}
      <div className={styles.list}>
        {justiceVotes.map((v) => (
          <JusticeVoteRow key={v.name} vote={v} />
        ))}
      </div>
    </div>
  );
}
