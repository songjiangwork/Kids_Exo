import { ComponentFixture, TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";
import { AssignmentNotebook } from "./assignment-notebook";
import { Assignment, OnlineCatalog } from "../core/practice-api";

const catalog: OnlineCatalog = {
  default_locale: "en-CA",
  question_counts: [10, 20, 30],
  feedback_modes: ["immediate", "deferred"],
  show_timer_configurable: true,
  plugins: [
    {
      plugin: "multiply_by_11",
      title: "Multiply by 11",
      description: "Practice multiplying by 11.",
      subject: "Math",
      category: "Mental Multiplication",
      default_locale: "en-CA",
      settings: [
        {
          name: "multiplicand_digits",
          label: "Number size",
          control: "single_choice",
          default: [2],
          options: [{ value: 2, label: "Two digits" }],
        },
      ],
      supported_delivery_modes: ["web_practice"],
    },
  ],
};

const assignments: Assignment[] = [
  {
    id: 4,
    learner_id: 1,
    title: "Multiply by 11 practice",
    description: "Finish today",
    status: "assigned",
    source_type: "parent_assigned",
    due_at: null,
    created_by_role: "parent",
    created_at: "2026-06-09T10:00:00Z",
    updated_at: "2026-06-09T10:00:00Z",
    completed_at: null,
    items: [
      {
        id: 9,
        item_type: "practice_plugin",
        plugin: "multiply_by_11",
        plugin_settings: { multiplicand_digits: [2] },
        question_count: 10,
        feedback_mode: "immediate",
        show_timer: true,
        order_index: 1,
        required: true,
        status: "assigned",
        linked_session_id: null,
        created_at: "2026-06-09T10:00:00Z",
        completed_at: null,
      },
    ],
  },
  {
    id: 5,
    learner_id: 1,
    title: "Completed assignment",
    description: "",
    status: "completed",
    source_type: "parent_assigned",
    due_at: null,
    created_by_role: "parent",
    created_at: "2026-06-09T11:00:00Z",
    updated_at: "2026-06-09T11:10:00Z",
    completed_at: "2026-06-09T11:10:00Z",
    items: [
      {
        id: 10,
        item_type: "practice_plugin",
        plugin: "multiply_by_11",
        plugin_settings: { multiplicand_digits: [2] },
        question_count: 10,
        feedback_mode: "immediate",
        show_timer: true,
        order_index: 1,
        required: true,
        status: "completed",
        linked_session_id: 7,
        student_token: "s7-abcd2345",
        created_at: "2026-06-09T11:00:00Z",
        completed_at: "2026-06-09T11:10:00Z",
      },
    ],
  },
];

describe("AssignmentNotebook", () => {
  let fixture: ComponentFixture<AssignmentNotebook>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssignmentNotebook],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(AssignmentNotebook);
    fixture.componentRef.setInput("catalog", catalog);
    fixture.componentRef.setInput("assignments", assignments);
    fixture.detectChanges();
  });

  it("renders assignment table rows and completed status", () => {
    expect(fixture.nativeElement.textContent).toContain("Description / notes (optional)");
    expect(fixture.nativeElement.textContent).toContain("Multiply by 11 practice");
    expect(fixture.nativeElement.textContent).toContain("Completed assignment");
    expect(fixture.nativeElement.textContent).toContain("Completed");
    expect(fixture.nativeElement.textContent).toContain("Multiply by 11 - 10 questions");
  });

  it("emits start action for assigned homework", () => {
    const emitted: unknown[] = [];
    fixture.componentInstance.startAssignmentItem.subscribe((value) => emitted.push(value));

    const startButton = Array.from(fixture.nativeElement.querySelectorAll("button") as NodeListOf<HTMLButtonElement>).find((button) =>
      button.textContent?.includes("Start / Continue"),
    ) as HTMLButtonElement;
    startButton.click();

    expect(emitted.length).toBe(1);
    expect((emitted[0] as any).assignment.id).toBe(4);
    expect((emitted[0] as any).item.id).toBe(9);
  });
});
