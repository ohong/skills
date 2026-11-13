# Smart Brevity before/after examples

Each example shows the source, the rewrite, and the moves that mattered.

## 1. AI chat answer

**Before**

> Great question! Choosing between PostgreSQL and MongoDB is an important decision that depends on a wide range of factors. It's worth noting that both databases are robust, mature solutions with thriving communities. PostgreSQL is a relational database that excels at complex queries and data integrity, while MongoDB is a document database that offers flexibility and scalability. In your case, since you mentioned your data is highly relational with lots of joins between users, orders, and products, PostgreSQL would likely be the better choice. However, if your schema changes frequently, MongoDB might be worth considering. Ultimately, the best choice depends on your specific needs. I hope this helps! Let me know if you have any other questions.

**After**

> **Use PostgreSQL.** Your users, orders and products are joined constantly, and relational joins and integrity constraints are what Postgres does best.
>
> **Yes, but:** if your schema still changes weekly, Postgres `jsonb` columns give you document-style flexibility without switching databases.

**Moves:** answer moved to sentence one; generic praise and both-sides filler cut; "might be worth considering" became a concrete alternative; ritual closer deleted.

## 2. Corporate email

**Before**

> Subject: Follow-up regarding our ongoing office transition process
>
> Hi everyone, I hope you're all doing well. I wanted to reach out to provide another update regarding the office transition we have been discussing over the past several weeks. As you know, we have been assessing several possible dates for the move. After reviewing all of these factors, we have decided that the office will close on Friday 17 October so the move can take place over the weekend. We are therefore asking everyone to take laptops and personal items home before leaving on Thursday. Please let me know if you have any questions.

**After**

> **Subject: Office closes Friday, Oct. 17**
>
> **The office will close Friday, Oct. 17, for our move.**
>
> **What you need to do:** Take your laptop and personal items home when you leave Thursday.
>
> **What's next:** Facilities will send Monday access instructions next week. *[confirm owner/date]*

**Moves:** label subject became news; decision moved from sentence five to sentence one; known history and pleasantries cut; non-close replaced with a next step, flagged because the source didn't state it.

## 3. Executive update

**Before**

> The commercial team has had a good month. Work on pricing continued and a number of customer conversations were positive. We have also been examining retention trends, and there has been some progress on enterprise renewals. Revenue for the quarter is currently £12.6 million versus our £12.1 million plan. Three renewals worth £1.8 million remain unresolved and will determine whether we finish materially above plan.

**After**

> **Q3 revenue is £0.5m above plan.**
>
> Revenue is **£12.6m vs. £12.1m planned**, helped by pricing and enterprise renewals.
>
> **Why it matters:** Three open renewals worth £1.8m decide whether we finish well above plan.

**Moves:** the buried number became the headline; the number got its comparison; vague activity ("work continued", "conversations were positive") cut.

## 4. Restraint: already-good analysis

**Before**

> The evidence does not support the claim that remote work consistently reduces productivity. Several observational studies report lower output in some settings, while controlled studies have found neutral or positive effects elsewhere. Outcomes depend heavily on job design, measurement and implementation.

**After**

> **Remote work has no single, consistent productivity effect.** Studies find negative, neutral and positive results depending on job design, measurement and implementation.

**Moves:** light touch only. The conditional "depending on..." *is* the finding; cutting it to make the claim punchier would make it false.

## 5. Sensitive message

**Before**

> I wanted to take a moment to share some difficult news. As many of you know, the company has been navigating a challenging macroeconomic environment, and leadership has been evaluating various options. After careful consideration, we have made the very hard decision to reduce the size of the team by 12 people, effective today. Affected employees will receive an email from HR within the hour.

**After**

> **We're laying off 12 people today.** This is a hard decision, and I'm sorry to the colleagues it affects.
>
> If you're affected, HR will email you within the hour. *[Add: where people can ask questions, and when.]*

**Moves:** news first, but the apology stays, because tone is part of the information here. The "challenging environment" preamble goes; if the reason matters, state it plainly in one sentence. The missing support channel is flagged, not invented.
